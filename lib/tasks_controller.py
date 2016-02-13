import os
import json
import psutil
from tornado.ioloop import PeriodicCallback
import logging
import re

from lib.tasks_scheduler import TasksScheduler
from lib.file_history_storage import FileHistoryStorage
from lib.task_run import TaskRun
from lib.notifier import Notifier


class TaskController():
    SHELL_SCRIPT_RE = r'(.+\.sh)'

    def __init__(self, tasks_dir="etc", history_dir="./var", notifier_config={}, notify_to='logger', websocket_clients=[]):
        self.tasks_dir = tasks_dir
        if not os.path.exists(self.tasks_dir):
            os.makedirs(self.tasks_dir)

        self.websocket_clients = websocket_clients
        self.history_storage = FileHistoryStorage(history_dir)
        self.notifier = Notifier(notifier_config=notifier_config,
            notify_to=notify_to,
            websocket_clients=websocket_clients)
        self.task_scheduler = TasksScheduler(tasks_dir=tasks_dir,
            history_storage=self.history_storage,
            notifier=self.notifier)
        self.check_dead_processes()
        self.process_checking_loop = PeriodicCallback(self.check_dead_processes, 10000)
        self.process_checking_loop.start()

    def update_config(self):
        return self.task_scheduler.update_config()

    def start(self):
        self.task_scheduler.start()

    def start_task_loop(self):
        self.task_scheduler.start_task_loop()

    def stop_task_loop(self):
        self.task_scheduler.stop_task_loop()

    def get_status(self):
        return self.task_scheduler.get_status()

    def check_dead_processes(self):
        logging.info('Checking dead processes')
        for currently_running_task in self.history_storage.get_currently_running_tasks():
            task_run = TaskRun.from_state(currently_running_task)

            if 'pid' in task_run.state:
                if psutil.pid_exists(task_run.state['pid']):
                    logging.info('Task %s with run %s is alive', task_run.task_id, task_run.id)
                else:
                    logging.info('Task %s with run %s is dead already; finalized', task_run.task_id, task_run.id)
                    self.history_storage.finalize_task_run(task_run)
                    self.notifier.error(task_run.get_found_dead_message())
            else:
                logging.info('Task %s with run %s is in unknown state, no pid; finalized', task_run.task_id, task_run.id)
                self.history_storage.finalize_task_run(task_run)
                self.notifier.error(task_run.get_found_dead_message())

    def get_next_tasks(self):
        return self.task_scheduler.get_next_tasks()

    def get_task_list(self, with_history=False):

        def extend_data(task):
            task['runs'] = self.get_detailed_history_for_task_id(task['name'])
            return task

        result = self.task_scheduler.tasks_list
        if with_history:
            result = [extend_data(task) for task in result]
        return result

    def get_recent_history(self, limit):
        return self.history_storage.get_recent_history(limit)

    def get_task_by_id(self, task_id):
        for task in self.task_scheduler.tasks_list:
            if task['name'] == task_id:
                task['shell_script_content'] = self.try_to_parse_task_shell_script(task['cmd'])
                return task
        return None

    def try_to_parse_task_shell_script(self, cmd):
        match = re.search(self.SHELL_SCRIPT_RE, cmd)
        if match:
            try:
                shell_script = match.group(1)
                with open(shell_script) as content:
                    return(content.read())
            except Exception:
                return None

        return None

    def set_task_by_id(self, task_id, task_config):
        # try to update task first
        task = self.get_task_by_id(task_id)
        if task:
            task.update(task_config)
            task_config = task

        f = open(self.tasks_dir + '/%s.json' % task_id, 'w')
        f.write(json.dumps(task_config))
        f.close()
        self.task_scheduler.check_config()
        return True

    def delete_task_by_id(self, task_id):
        f = self.tasks_dir + '/%s.json' % task_id
        os.remove(f)
        self.task_scheduler.check_config()
        return True

    def get_task_runs_for_task_id(self, task_id, limit=20):
        return self.history_storage.get_task_runs_for_task_id(task_id, limit)

    def get_detailed_history_for_task_id(self, task_id, limit=20):
        return self.history_storage.get_detailed_history_for_task_id(task_id, limit)

    def get_detailed_task_run_info(self, task_id, task_run_id):
        return self.history_storage.get_detailed_task_run_info(task_id, task_run_id)

    def run_task_by_task_id(self, task_id):
        task = self.get_task_by_id(task_id)
        logging.info('MANUAL RUN | Running %s task' % task['name'])
        self.task_scheduler.run_task_by_name_and_cmd(task['name'], task['cmd'])

    def get_tasks_config(self):
        return self.task_scheduler.get_tasks_config()

    def validate_config(self, config):
        return self.task_scheduler.validate_config(config)
