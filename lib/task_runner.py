import os
import time
import datetime
import sys
import subprocess
import json
import glob
import re
from crontab import CronTab
import logging

class TaskRunner():
    def __init__(self, taskname, history_storage):
        self.taskname = taskname
        self.history_storage = history_storage
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
        logging.info("Runner started, %s" % self.taskname)
        logging.info("Command: %s" % cmd)
        if not self.history_storage.task_valid_to_run(self.taskname):
            raise FileExistsError('%s task is in progress' % self.taskname)
        child_pid = os.fork()
        if child_pid == 0:
            os.setsid()
            inner_child_pid = os.fork()
            if inner_child_pid == 0:
                # child process
                task_run_id = self.get_human_readable_timestamp()

                self.history_storage.prepare_task_run(self.taskname, task_run_id)

                self.state['current'] = 'running'
                self.state['started_at'] = self.get_timestamp()
                self.history_storage.update_state_for_task_run_id(self.taskname, task_run_id, self.state)
                self.history_storage.update_current_task_run_for_task(self.taskname, task_run_id)
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                self.history_storage.update_pid_for_task_run_id(self.taskname, task_run_id, str(proc.pid))
                stdout, stderr = proc.communicate()
                self.state['exit_code'] = proc.returncode
                self.history_storage.update_stdout_for_task_run_id(self.taskname, task_run_id, stdout.decode())
                self.history_storage.update_stderr_for_task_run_id(self.taskname, task_run_id, stderr.decode())
                self.state['finished_at'] = self.get_timestamp()
                self.state['current'] = 'finished'
                self.history_storage.update_state_for_task_run_id(self.taskname, task_run_id, self.state)
                self.history_storage.delete_current_task_run_for_task(self.taskname)
                sys.exit(0)
            else:
                sys.exit(0)