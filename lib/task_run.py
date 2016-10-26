import time
import datetime
import signal
import psutil
import logging

def kill_pid(pid, sig=signal.SIGTERM):
    try:
      parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
      return
    children = parent.children(recursive=True)
    for process in children:
      process.send_signal(sig)
      try:
          process.send_signal(sig)
      except ProcessLookupError:
          continue
      logging.info("couldn't kill process by TERM signal, let's start use KILL")
      process.send_signal(signal.SIGKILL)

class TaskRun():
    def __init__(self, task_id):
        started_at = datetime.datetime.utcnow()
        self.task_id = task_id
        self.id = None

        self.state = {
            'current': 'running',
            'started_at': started_at.strftime('%Y-%m-%d %H:%M:%S'),
            'finished_at': None,
            'pid': None,
            'exit_code': None,
            'task_id': self.task_id
        }
        self.stdout = ''
        self.stderr = ''

    @classmethod
    def from_state(klass, state):
        task_run = klass(state['task_id'])
        task_run.id = state['task_run_id']
        task_run.state = state

        return task_run

    def shutdown(self):
        kill_pid(self.state['pid'])

    def finalize(self):
        finished_at = datetime.datetime.utcnow()
        self.state['finished_at'] = finished_at.strftime('%Y-%m-%d %H:%M:%S')
        self.state['current'] = 'finished'
