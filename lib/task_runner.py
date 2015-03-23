import os
import time
import datetime
import sys
import subprocess
import json
import glob
import re
from crontab import CronTab

class TaskRunner():
    def __init__(self, taskname):
        self.taskname = taskname
        self.state = {}

    def get_human_readable_timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S_%f')

    def get_timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    def get_state_as_json(self):
        return json.dumps(self.state)

    def to_file(self, path, str):
        with open(path, 'w') as f:
            f.write(str)

    def run_task(self, cmd):
        print("Runner started, %s" % self.taskname)
        print("Command: %s" % cmd)

        timestamp = self.get_human_readable_timestamp()

        task_path = './var/' + self.taskname
        if not os.path.isdir(task_path):
            os.makedirs(task_path)
        current_run_path = task_path + '/' + timestamp
        if not os.path.isdir(current_run_path):
            os.makedirs(current_run_path)

        new_pid = os.fork()
        if not new_pid  == 0:
            self.to_file(current_run_path + '/pid', str(new_pid))
        else:
            stdout = open(current_run_path + '/stdout', 'w')
            stderr = open(current_run_path + '/stderr', 'w')
            self.state['current'] = 'running'
            self.state['started_at'] = self.get_timestamp()
            self.to_file(current_run_path + '/state', self.get_state_as_json())
            self.to_file(task_path + '/current', timestamp)
            self.state['exit_code'] = subprocess.call(cmd, stdout=stdout, stderr=stderr, shell=True)
            self.state['finished_at'] = self.get_timestamp()
            self.state['current'] = 'finished'
            self.to_file(current_run_path + '/state', self.get_state_as_json())
            os.remove(task_path + '/current')
            sys.exit()
