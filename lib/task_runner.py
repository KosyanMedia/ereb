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
from lib.aa_subprocess import AASubprocess

class TaskRunner():
    def __init__(self, taskname, history_storage, notifier):
        self.taskname = taskname
        self.history_storage = history_storage
        self.notifier = notifier

    def run_task(self, cmd):
        logging.info("Runner started, %s" % self.taskname)
        logging.info("Command: %s" % cmd)
        if not self.history_storage.task_valid_to_run(self.taskname):
            raise FileExistsError('%s task is in progress' % self.taskname)

        self.task_run = TaskRun(self.taskname)
        self.history_storage.prepare_task_run(self.task_run)
        self.history_storage.update_state_for_task_run(self.task_run)
        self.history_storage.update_current_task_run_for_task(self.task_run)

        self.proc = AASubprocess(cmd, 5, self.chunk_stdout, self.chunk_stderr, self.done_callback)
        self.task_run.state['pid'] = self.proc.pid
        self.history_storage.update_state_for_task_run(self.task_run)

        self.proc.set_exit_callback(self.exit_callback)

    def chunk_stdout(self, data):
        self.task_run.stdout += data.decode()
        self.history_storage.update_stdout_for_task_run_id(self.task_run)

    def chunk_stderr(self, data):
        self.task_run.stderr += data.decode()
        self.history_storage.update_stderr_for_task_run_id(self.task_run)

    def done_callback(self, returncode, expired):
        self.proc.stdout.close()
        self.proc.stderr.close()

        self.task_run.state['exit_code'] = returncode
        self.task_run.finalize()
        self.history_storage.update_state_for_task_run(self.task_run)
        self.history_storage.delete_current_task_run_for_task(self.task_run)

        if returncode != 0:
            self.notifier.error(self.task_run.get_error_message())
