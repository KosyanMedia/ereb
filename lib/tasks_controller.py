import os
import time
import datetime
import sys
import subprocess
import json
import glob
import re
from crontab import CronTab

from lib.task_runner import TaskRunner


class TaskController():
    def __init__(self):
        self.tasks_list = {}
        print("Starting")
        self.update_config()

    def update_config(self):
        new_config = self.get_tasks_config()
        result = new_config != self.tasks_list
        self.tasks_list = new_config
        return result

    def loop(self):
        while 1:
            if self.update_config():
                print("Config changed!")
            tasks_by_schedule = {}
            now = time.time()
            for task in self.tasks_list:
                next = CronTab(task['cron_schedule']).next(now)
                if next in tasks_by_schedule:
                    tasks_by_schedule[next].append(task)
                else:
                    tasks_by_schedule[next] = [task]

            next_tasks_with_crontab = sorted(tasks_by_schedule.items(), key=lambda x: x[0] )[0]
            next_run = next_tasks_with_crontab[0]
            next_tasks = next_tasks_with_crontab[1]
            print('Next run in %s seconds' % str(next_run))
            time.sleep(next_run)
            print('Now running %s tasks' % len(next_tasks))
            for task in next_tasks:
                print('Running %s task' % task['name'])
                TaskRunner(task['name']).run_task(task['cmd'])

    def get_tasks_config(self):
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
