# coding: utf-8

import logging

from ereb.task_run import TaskRun
from ereb.aa_subprocess import AASubprocess


class TaskRunner:
    def __init__(self, taskname, history_storage, notifier, on_error_callback):
        self.taskname = taskname
        self.history_storage = history_storage
        self.notifier = notifier
        self.on_error_callback = on_error_callback

    def run_task(self, cmd, timeout=-1):
        logging.info(
            "Runner started, %s with timeout %s", self.taskname, timeout)
        logging.info("Command: %s" % cmd)

        timeout = int(timeout)

        if not self.history_storage.task_valid_to_run(self.taskname):
            raise FileExistsError('%s task is in progress' % self.taskname)

        self.task_run = TaskRun(self.taskname)
        self.history_storage.prepare_task_run(self.task_run)
        self.history_storage.update_state_for_task_run(self.task_run)

        self.proc = AASubprocess(
            cmd, timeout, self.chunk_stdout, self.chunk_stderr,
            self.done_callback, kill_on_timeout=True)
        self.task_run.state['pid'] = self.proc.pid
        self.history_storage.update_state_for_task_run(self.task_run)

    def chunk_stdout(self, data):
        self.task_run.stdout += data.decode()
        self.history_storage.update_stdout_for_task_run_id(self.task_run)

    def chunk_stderr(self, data):
        self.task_run.stderr += data.decode()
        self.history_storage.update_stderr_for_task_run_id(self.task_run)

    def done_callback(self, return_code, expired):
        self.task_run.state['exit_code'] = return_code
        self.task_run.finalize()
        self.history_storage.update_state_for_task_run(self.task_run)

        if return_code != 0:
            self.on_error_callback(self.taskname, return_code)
            self.notifier.send_failed_task_run(self.task_run)
