import os
import time
import datetime
import sys
import subprocess
import json
import glob
import re
from crontab import CronTab
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen

from lib.task_runner import TaskRunner


class TaskController():
    def __init__(self):
        self.tasks_list = {}
        self.is_task_loop_running = False
        self.pending_tasks = []
        print("Starting")
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

    def get_status(self):
        result = {}
        if self.is_task_loop_running:
            result['state'] = 'running'
        else:
            result['state'] = 'stopped'

        result['next_run'], result['next_tasks'] = self.get_next_tasks()

        return result

    def get_next_tasks(self):
        next_run, next_tasks = self.get_next_tasks()
        return { 'next_run': next_run, 'next_tasks': next_tasks}

    def get_task_list(self):
        return self.tasks_list

    def get_task_by_id(self, task_id):
        result = None
        for task in self.tasks_list:
            if task['name'] == task_id:
                return task
        return result

    def set_task_by_id(self, task_id, task_config):
        f = open('./etc/%s.json' % task_id, 'w')
        f.write(json.dumps(task_config))
        f.close()
        self.update_config()
        return True

    def delete_task_by_id(self, task_id):
        f = './etc/%s.json' % task_id
        os.remove(f)
        self.update_config()
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
        TaskRunner(task['name']).run_task(task['cmd'])

    @gen.engine
    def check_config(self):
        if self.update_config():
            print("Config changed!")

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

    @gen.engine
    def schedule_next_tasks(self):
        if self.is_task_loop_running:
            print("TaskRunner running")
            next_run, next_tasks = self.get_next_tasks()
            print('Next run in %s seconds' % str(next_run))
            yield gen.Task(IOLoop.instance().add_timeout, time.time() + next_run)
            print('Now running %s tasks' % len(next_tasks))
            for task in next_tasks:
                print('Running %s task' % task['name'])
                TaskRunner(task['name']).run_task(task['cmd'])
            print('is running? %s' % self.is_task_loop_running)
            IOLoop.instance().add_callback(self.schedule_next_tasks)
        else:
            print("TaskRunner stopped")

    def get_next_tasks(self):
        tasks_by_schedule = {}
        now = time.time()
        for task in self.tasks_list:
            next = CronTab(task['cron_schedule']).next(now)
            if next in tasks_by_schedule:
                tasks_by_schedule[next].append(task)
            else:
                tasks_by_schedule[next] = [task]
        return sorted(tasks_by_schedule.items(), key=lambda x: x[0] )[0]
