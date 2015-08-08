import os
import time
import datetime
import sys
import subprocess
import json
import glob
import re
import uuid
from crontab import CronTab
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
import logging

from lib.task_runner import TaskRunner

class TasksScheduler():
    def __init__(self, tasks_dir, history_storage):
        self.tasks_dir = tasks_dir
        self.history_storage = history_storage
        self.tasks_list = {}
        self.is_task_loop_running = False
        self.planned_task_run_uuids = []
        self.update_config()

    def update_config(self):
        new_config = self.get_tasks_config()
        result = new_config != self.tasks_list
        self.tasks_list = new_config
        return result

    def start(self):
        self.config_checking_loop = PeriodicCallback(self.check_config, 1000)
        self.config_checking_loop.start()
        self.start_task_loop()

    def start_task_loop(self):
        self.is_task_loop_running = True
        IOLoop.instance().add_callback(self.schedule_next_tasks)

    def stop_task_loop(self):
        self.is_task_loop_running = False
        self.planned_task_run_uuids = []

    def run_task_by_name_and_cmd(self, name, cmd):
        logging.info('Manual run | Running %s task' % name)
        # try:
        TaskRunner(name, self.history_storage).run_task(cmd)
        # except Exception as e:
            # logging.error('Manual task run error. %s' % e)

    @gen.engine
    def check_config(self):
        if self.update_config():
            logging.info("Config changed!")
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
            next_time = CronTab(config['cron_schedule']).next()
            result = next_time and isinstance(config, dict) and 'cron_schedule' in config and 'cmd' in config
        except:
            logging.info("BadConfigException: %s" % config)
            result = False

        return result

    @gen.engine
    def schedule_next_tasks(self):
        if self.is_task_loop_running:
            logging.info("TaskRunner running")
            next_run, next_tasks = self.get_next_tasks()
            if len(next_tasks) > 0:
                logging.info('Next run in %s seconds' % str(next_run))
                task_run_uuid = str(uuid.uuid4())
                self.planned_task_run_uuids.append(task_run_uuid)
                logging.info('Planned task %s' % task_run_uuid)
                yield gen.Task(IOLoop.instance().add_timeout, time.time() + next_run)
                if task_run_uuid in self.planned_task_run_uuids:
                    logging.info('Now running %s tasks' % len(next_tasks))
                    for task in next_tasks:
                        try:
                            logging.info('Running %s task' % task['name'])
                            TaskRunner(task['name'], self.history_storage).run_task(task['cmd'])
                        except Exception as e:
                            logging.error('Scheduled task run error. %s' % e)
                    self.planned_task_run_uuids.remove(task_run_uuid)
                    logging.info('Run and removed task run %s' % task_run_uuid)
                    IOLoop.instance().add_callback(self.schedule_next_tasks)
                else:
                    logging.info('Task run %s was cancelled' % task_run_uuid)
        else:
            logging.info("TaskRunner stopped")

    def get_next_tasks(self):
        tasks_by_schedule = {}
        now = time.time()
        for task in self.tasks_list:
            next = CronTab(task['cron_schedule']).next(now)
            if next in tasks_by_schedule:
                tasks_by_schedule[next].append(task)
            else:
                tasks_by_schedule[next] = [task]
        if len(tasks_by_schedule) > 0:
            return sorted(tasks_by_schedule.items(), key=lambda x: x[0] )[0]
        else:
            return [0, []]
