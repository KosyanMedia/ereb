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

from lib.tasks_scheduler import TasksScheduler

class TaskController():
    def __init__(self):
        print("Starting TaskController")
        self.task_scheduler = TasksScheduler()

    def update_config(self):
        return self.task_scheduler.update_config()

    def start(self):
        self.task_scheduler.start()

    def start_task_loop(self):
        self.task_scheduler.start()

    def stop_task_loop(self):
        self.task_scheduler.stop()

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

    def get_task_list(self):
        return self.task_scheduler.tasks_list

    def get_task_by_id(self, task_id):
        result = None
        for task in self.task_scheduler.tasks_list:
            if task['name'] == task_id:
                return task
        return result

    def set_task_by_id(self, task_id, task_config):
        f = open('./etc/%s.json' % task_id, 'w')
        f.write(json.dumps(task_config))
        f.close()
        self.task_scheduler.update_config()
        return True

    def delete_task_by_id(self, task_id):
        f = './etc/%s.json' % task_id
        os.remove(f)
        self.task_scheduler.update_config()
        return True

    def get_task_runs_for_task_id(self, task_id):
        task_run_files = glob.glob('./var/%s/*/state' % task_id)
        result = {}
        regexp = re.compile('./[^/]+/[^/]+/([^/]+)/state', re.IGNORECASE)
        for f in task_run_files:
            task_run_id = regexp.search(f).group(1)
            with open(f) as task_run_file:
                result[task_run_id] = json.load(task_run_file)

        return result

    def get_detailed_history_for_task_id(self, task_id):
        task_run_dirs = glob.glob('./var/%s/*' % task_id)
        result = {}
        regexp = re.compile('./[^/]+/[^/]+/([^/]+)$', re.IGNORECASE)
        for f in task_run_dirs:
            task_run_id = regexp.search(f).group(1)
            task_run = {}

            with open(f + '/state') as file_content:
                task_run['state'] = json.load(file_content)
            for x in ['stdout', 'stderr', 'pid']:
                with open(f + '/' + x) as file_content:
                    task_run[x] = file_content.read()
            result[task_run_id] = task_run

        return result

    def run_task_by_task_id(self, task_id):
        task = self.get_task_by_id(task_id)
        print('MANUAL RUN | Running %s task' % task['name'])
        self.task_scheduler.run_task_by_name_and_cmd(task['name'], task['cmd'])

    def get_tasks_config(self):
        # async?
        regexp = re.compile('.+\/(.+).json', re.IGNORECASE)
        config = []
        for f in glob.glob('./etc/*.json'):
            try:
                task_name = regexp.search(f).group(1)
                with open(f) as config_file:
                    c = json.load(config_file)
                if self.validate_config(c):
                    c['name'] = task_name
                    config.append(c)
                else:
                    print("Something bad with %s config file" % f)
            except Exception:
                print("Error loading %s config file" % f)
        return config

    def validate_config(self, config):
        return isinstance(config, dict) and 'cron_schedule' in config and 'cmd' in config

