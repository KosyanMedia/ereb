import time
import json
import glob
import re
import uuid
from crontab import CronTab
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
import logging
from os.path import isfile
from datadog import statsd

from ereb.task_runner import TaskRunner


class TasksScheduler():
    SHELL_SCRIPT_RE = r'(\S+\.(sh|rb|py))'

    def __init__(self, tasks_dir, history_storage, notifier, datadog_metrics):
        self.tasks_dir = tasks_dir
        self.history_storage = history_storage
        self.notifier = notifier
        self.datadog_metrics = datadog_metrics
        self.tasks_list = []
        self.is_task_loop_running = False
        self.planned_task_run_uuids = []
        self.try_after_fail_tasks = {}
        self.try_after_fail_tries_count = 2
        self.try_after_fail_interval = 60  # 6
        self.task_queue_by_timestamp = {}
        self.update_config()

    def update_config(self):
        new_config = self.get_tasks_config()
        old_tasks_by_id = {}
        new_tasks_by_id = {}
        for old_task in self.tasks_list:
            old_tasks_by_id[old_task['name']] = {
                'cron_schedule': old_task.get('cron_schedule'),
                'cmd': old_task.get('cmd'),
                'try_more_on_error': old_task.get('try_more_on_error')
            }
        for new_task in new_config:
            new_tasks_by_id[new_task['name']] = {
                'cron_schedule': new_task.get('cron_schedule'),
                'cmd': new_task.get('cmd'),
                'try_more_on_error': new_task.get('try_more_on_error')
            }

        if new_tasks_by_id != old_tasks_by_id:
            self.tasks_list = new_config
            return True

    def get_task_config(self, name):
        for config in self.tasks_list:
            if config['name'] == name:
                return config
        return None

    def start(self):
        self.config_checking_loop = PeriodicCallback(self.check_config, 1 * 1000)
        self.config_checking_loop.start()
        self.start_task_loop()

    def start_task_loop(self):
        self.is_task_loop_running = True
        IOLoop.instance().add_callback(self.schedule_next_tasks)

    def stop_task_loop(self):
        self.is_task_loop_running = False
        self.planned_task_run_uuids = []

    def run_task_by_name_and_cmd(self, name, cmd, timeout):
        logging.info('Manual run | Running %s task' % name)
        try:
            task_runner = TaskRunner(name, self.history_storage, self.notifier,
                                     self.on_task_fail_callback, self.datadog_metrics)
            task_runner.run_task(cmd, timeout)
        except Exception as e:
            logging.error('Manual task run error. %s' % e)

    def on_task_fail_callback(self, task_id, return_code):
        def add_failed_task_to_queue(task_id):
            next_run = time.time() + self.try_after_fail_interval
            if next_run in self.task_queue_by_timestamp:
                self.task_queue_by_timestamp[next_run].append(task_id)
            else:
                self.task_queue_by_timestamp[next_run] = [task_id]

        task = self.get_task_by_id(task_id, False)
        if task and task.get('try_more_on_error', False):
            if task_id in self.try_after_fail_tasks:
                self.try_after_fail_tasks[task_id] -= 1
                if self.try_after_fail_tasks[task_id] == 0:
                    # no more tries
                    self.try_after_fail_tasks.pop(task_id)
                    self.reschedule_tasks()
                else:
                    add_failed_task_to_queue(task_id)
                    self.reschedule_tasks()
            else:
                self.try_after_fail_tasks[task_id] = self.try_after_fail_tries_count

                add_failed_task_to_queue(task_id)
                self.reschedule_tasks()

    @gen.engine
    def check_config(self):
        if self.update_config():
            logging.info("Config changed")
            self.reschedule_tasks()

    @gen.engine
    def reschedule_tasks(self):
        logging.info("Recheduling tasks!")
        self.planned_task_run_uuids = []
        IOLoop.instance().add_callback(self.schedule_next_tasks)

    def get_tasks_config(self):
        # async?
        regexp = re.compile('.+\/(.+).json', re.IGNORECASE)
        config = []
        for f in glob.glob(self.tasks_dir + '/*.json'):
            try:
                task_name = regexp.search(f).group(1)
                with open(f) as config_file:
                    c = json.load(config_file)
                if self.validate_config(c):
                    c['name'] = task_name
                    config.append(c)
                else:
                    logging.info("Something bad with %s config file" % f)
            except Exception:
                logging.info("Error loading %s config file" % f)

        return config

    def validate_config(self, config):
        try:
            if 'cron_schedule' in config:
                next_time = CronTab(config['cron_schedule']).next(default_utc=True)
            result = isinstance(config, dict)
        except:
            logging.info("BadConfigException: %s" % config)
            result = False

        return result

    def get_status(self):
        result = {}
        if self.is_task_loop_running:
            result['state'] = 'running'
        else:
            result['state'] = 'stopped'

        result['next_run'], result['next_tasks'] = self.get_next_tasks()
        result['planned_task_run_uuids'] = self.planned_task_run_uuids

        return result

    @gen.engine
    def schedule_next_tasks(self):
        if self.is_task_loop_running:
            logging.info("Tasks loop started")
            self.notifier.websocket_send_status(self.get_status())
            next_run, next_tasks = self.get_next_tasks()
            if len(next_tasks) > 0:
                logging.info('Next run in %s seconds' % str(next_run))
                task_run_uuid = str(uuid.uuid4())
                self.planned_task_run_uuids.append(task_run_uuid)  # allows to cancel already scheduled tasks
                logging.info('Planned task %s' % task_run_uuid)
                # wait until next task needs to be run, and while waiting -
                # do other stuff in IOLoop (i.e. process web interface requests)
                yield gen.Task(IOLoop.instance().add_timeout, time.time() + next_run)
                if task_run_uuid in self.planned_task_run_uuids:
                    logging.info('Now running %s tasks' % len(next_tasks))
                    for task in next_tasks:
                        try:
                            logging.info('Running %s task with timeout %s', task['name'], task.get('timeout', -1))
                            task_runner = TaskRunner(task['name'], self.history_storage,
                                                     self.notifier, self.on_task_fail_callback, self.datadog_metrics)
                            task_runner.run_task(task['cmd'], task.get('`timeout', -1))
                        except Exception as e:
                            logging.exception('Scheduled task run error %s' % task['name'])
                    self.planned_task_run_uuids.remove(task_run_uuid)
                    logging.info('Run and removed task run %s' % task_run_uuid)
                    IOLoop.instance().add_callback(self.schedule_next_tasks)
                else:
                    logging.info('Task %s run %s was cancelled for ' % (task['name'], task_run_uuid))
            self.clean_task_queue_by_timestamp()
        else:
            logging.info("TaskRunner stopped")

    def get_next_tasks(self):
        tasks_by_schedule = {}
        now = time.time()

        for task in self.tasks_list:
            if task.get('enabled', False):
                next = CronTab(task['cron_schedule']).next(now, default_utc=True)
                if next in tasks_by_schedule:
                    tasks_by_schedule[next].append(task)
                else:
                    tasks_by_schedule[next] = [task]

        for next_timestamp, tasks in self.task_queue_by_timestamp.items():
            next = next_timestamp - time.time()
            for task_id in tasks:
                task = self.get_task_by_id(task_id, False)
                if next in tasks_by_schedule:
                    tasks_by_schedule[next].append(task)
                else:
                    tasks_by_schedule[next] = [task]

        if len(tasks_by_schedule) > 0:
            return sorted(tasks_by_schedule.items(), key=lambda x: x[0])[0]
        else:
            return [0, []]

    def get_task_by_id(self, task_id, with_extra_info=False):
        for task in self.tasks_list:
            if task['name'] == task_id:
                task['shell_scripts'] = []
                if with_extra_info:
                    task['shell_scripts'] = self.try_to_parse_task_shell_script(task['cmd'])

                return task

        return None

    def clean_task_queue_by_timestamp(self):
        for next_timestamp in list(self.task_queue_by_timestamp.keys()):
            if time.time() > next_timestamp:
                del self.task_queue_by_timestamp[next_timestamp]

    def try_to_parse_task_shell_script(self, cmd):
        scripts = list(map(lambda x: x[0], re.findall(self.SHELL_SCRIPT_RE, cmd)))
        def read_file(shell_script):
            with open(shell_script, 'r', encoding='utf8') as content:
                return {'filename': shell_script, 'content': content.read()}
        return_data = []
        for script in scripts:
            if isfile(script):
                return_data.append(read_file(script))
        return return_data
