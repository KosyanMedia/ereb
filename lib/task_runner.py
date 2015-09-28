import os
import time
import datetime
import sys
import subprocess
import json
import glob
import re
import signal
from crontab import CronTab
import logging


from lib.task_run import TaskRun

class TaskRunner():
    def __init__(self, taskname, history_storage, notifier):
        self.taskname = taskname
        self.history_storage = history_storage
        self.notifier = notifier
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

        handler = signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        child_pid = os.fork()
        if child_pid == 0:
            # child process
            # os.setsid()

            task_run = TaskRun(self.taskname)

            self.history_storage.prepare_task_run(task_run)

            self.history_storage.update_state_for_task_run(task_run)
            self.history_storage.update_current_task_run_for_task(task_run)

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            task_run.state['pid'] = proc.pid
            self.history_storage.update_state_for_task_run(task_run)
            stdout, stderr = proc.communicate()

            task_run.state['exit_code'] = proc.returncode
            task_run.stdout = stdout.decode()
            self.history_storage.update_stdout_for_task_run_id(task_run)

            task_run.stderr = stderr.decode()
            self.history_storage.update_stderr_for_task_run_id(task_run)

            task_run.finalize()

            self.history_storage.update_state_for_task_run(task_run)
            self.history_storage.delete_current_task_run_for_task(task_run)

            if int(proc.returncode) != 0:
                self.notifier.error(task_run.get_error_message())

            os._exit(0)
