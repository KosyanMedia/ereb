import time
import datetime


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

    def finalize(self):
        finished_at = datetime.datetime.utcnow()
        self.state['finished_at'] = finished_at.strftime('%Y-%m-%d %H:%M:%S')
        self.state['current'] = 'finished'
