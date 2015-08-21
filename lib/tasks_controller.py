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


from lib.tasks_scheduler import TasksScheduler
from lib.file_history_storage import FileHistoryStorage

class TaskController():
    def __init__(self, tasks_dir="etc", history_dir="./var"):
        self.tasks_dir = tasks_dir
        self.history_storage = FileHistoryStorage(history_dir)
        self.task_scheduler = TasksScheduler(tasks_dir, self.history_storage)

    def update_config(self):
        return self.task_scheduler.update_config()

    def start(self):
        self.task_scheduler.start()

    def start_task_loop(self):
        self.task_scheduler.start_task_loop()

    def stop_task_loop(self):
        self.task_scheduler.stop_task_loop()

    def get_status(self):
        result = {}
        if self.task_scheduler.is_task_loop_running:
            result['state'] = 'running'
        else:
            result['state'] = 'stopped'

        result['next_run'], result['next_tasks'] = self.get_next_tasks()
        result['planned_task_run_uuids'] = self.task_scheduler.planned_task_run_uuids

        return result

    def get_next_tasks(self):
        return self.task_scheduler.get_next_tasks()

    def get_task_list(self, with_history):

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
        result = None
        for task in self.task_scheduler.tasks_list:
            if task['name'] == task_id:
                return task
        return result

    def set_task_by_id(self, task_id, task_config):
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
