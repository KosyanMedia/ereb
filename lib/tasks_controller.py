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
        if self.is_task_loop_running:
            r = "running"
        else:
            r = "stopped"
        return r


    @gen.engine
    def check_config(self):
        if self.update_config():
            print("Config changed!")

    def get_tasks_config(self):
        # async?
        regexp = re.compile('.+\/(.+).json', re.IGNORECASE)
        re.search('.+\/(.+).json', './etc/foo.json').groups(0)[0]
        config = []
        for f in glob.glob('./etc/*.json'):
            task_name = regexp.search(f).group(1)
            with open(f) as config_file:
                c = json.load(config_file)
            c['name'] = task_name
            config.append(c)
        return config

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
