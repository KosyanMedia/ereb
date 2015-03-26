from tornado.ioloop import IOLoop
from tornado import gen
import tornado.web
from lib.task_runner import TaskRunner
from lib.tasks_controller import TaskController
import time
import json

task_controller = TaskController()

class TasksListHandler(tornado.web.RequestHandler):
    def get(self):
        task_list = task_controller.get_task_list()
        self.write(task_list)

class TasksHandler(tornado.web.RequestHandler):
    def get(self, task_id, action):
        result = '404'
        if task_id == '' and action == '':
            result = json.dumps(task_controller.get_task_list())
        elif task_id != '':
            task = task_controller.get_task_by_id(task_id)
            if not task:
                self.raise_404('task %s not found' % task_id)
            if action == '':
                result = json.dumps({
                    'config': task,
                    'runs': task_controller.get_task_runs_for_task_id(task_id)
                })
            elif action == 'run':
                task_controller.run_task_by_task_id(task_id)
                result = 'task_run'
            elif action == 'history':
                result = json.dumps(task_controller.get_detailed_history_for_task_id(task_id))

        self.write(result)

    def raise_404(self, message):
        self.clear()
        self.set_status(404)
        self.finish("<html><body> %s </body></html>" % message)



class RunnerHandler(tornado.web.RequestHandler):
    def get(self, cmd):
        result = '404'
        if cmd == 'status':
            result = task_controller.get_status()
        elif cmd == 'start':
            task_controller.start_task_loop()
            result = 'started'
        elif cmd == 'stop':
            tasks_controller.stop_task_loop()
            result = 'stopped'
        self.write(result)

application = tornado.web.Application([
    (r"/tasks/?([^/]*)/?([^/]*)$", TasksHandler),
    (r"runner/(.+)$", RunnerHandler)
])

if __name__ == "__main__":

    # task_controller.start()
    application.listen(8888)

    IOLoop.instance().start()
