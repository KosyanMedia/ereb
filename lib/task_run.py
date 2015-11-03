import time
import datetime


class TaskRun():
    def __init__(self, task_id):
        started_at = datetime.datetime.fromtimestamp(time.time())
        self.task_id = task_id
        self.id = started_at.strftime('%Y_%m_%d_%H_%M_%S_%f')

        self.state = {
            'current': 'running',
            'started_at': started_at.strftime('%Y-%m-%d %H:%M:%S'),
            'task_id': self.task_id,
            'task_run_id': self.id,
            'day_of_start': started_at.strftime('%Y_%m_%d')
        }
        self.stdout = None
        self.stderr = None

    @classmethod
    def from_state(klass, state):
        task_run = klass(state['task_id'])
        task_run.id = state['task_run_id']
        task_run.state = state

        return task_run

    def finalize(self):
        finished_at = datetime.datetime.fromtimestamp(time.time())
        self.state['finished_at'] = finished_at.strftime('%Y-%m-%d %H:%M:%S')
        self.state['current'] = 'finished'

    def get_error_message(self):
        return "Task [{0}]/{1} failed".format(self.task_id, self.id)

    def get_found_dead_message(self):
        return "Task [{0}]/{1} was found dead and finalized".format(self.task_id, self.id)
