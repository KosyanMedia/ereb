import logging
import tornado.process


from lib.task_run import TaskRun


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

        self.proc = tornado.process.Subprocess(cmd, stdout=tornado.process.Subprocess.STREAM, stderr=tornado.process.Subprocess.STREAM, shell=True)
        self.task_run.state['pid'] = self.proc.pid
        self.history_storage.update_state_for_task_run(self.task_run)

        self.proc.set_exit_callback(self.exit_callback)

    def exit_callback(self, returncode):
        stdout = self.proc.stdout.read_from_fd()
        self.proc.stdout.close()
        if stdout:
            self.task_run.stdout = stdout.decode()
            self.history_storage.update_stdout_for_task_run_id(self.task_run)

        stderr = self.proc.stderr.read_from_fd()
        self.proc.stderr.close()
        if stderr:
            self.task_run.stderr = stderr.decode()
            self.history_storage.update_stderr_for_task_run_id(self.task_run)

        self.task_run.state['exit_code'] = returncode
        self.task_run.finalize()
        self.history_storage.update_state_for_task_run(self.task_run)
        self.history_storage.delete_current_task_run_for_task(self.task_run)

        if returncode != 0:
            self.notifier.error(self.task_run.get_error_message())
