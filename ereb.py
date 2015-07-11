from tornado.ioloop import IOLoop
from tornado import gen
import tornado.web
from lib.task_runner import TaskRunner
from lib.tasks_controller import TaskController
import time
import json

task_controller = TaskController()

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

        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(result)

    def post(self, task_id, action):
        result = '404'
        config = json.loads(self.request.body.decode())
        if task_id == '' and action == '':
            self.raise_404('Unknown route')
        elif task_id != '':
            task = task_controller.set_task_by_id(task_id, config)
            if not task:
                self.raise_500('Cannot update task with config: %s' % json.dumps(config))
            else:
                result = 'Success'

        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(result)

    def delete(self, task_id, action):
        result = '404'
        if task_id == '' and action == '':
            self.raise_404('Unknown route')
        elif task_id != '':
            task = task_controller.delete_task_by_id(task_id)
            if not task:
                self.raise_500('Cannot delete task with config: %s' % json.dumps(config))
            else:
                result = 'Success'
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(result)

    def raise_404(self, message):
        self.clear()
        self.set_status(404)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish(message)

    def raise_500(self, message):
        self.clear()
        self.set_status(500)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish(message)


class RunnerHandler(tornado.web.RequestHandler):
    def get(self, cmd):
        if cmd == '':
            result = json.dumps(task_controller.get_status())
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write(result)
        if cmd == 'recent_history':
            result = json.dumps(task_controller.get_recent_history(20))
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write(result)
        elif cmd == 'start':
            task_controller.start_task_loop()
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write('Success')
        elif cmd == 'stop':
            task_controller.stop_task_loop()
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write('Success')

application = tornado.web.Application([
    (r"/tasks/?([^/]*)/?([^/]*)$", TasksHandler),
    (r"/status/?(.*)$", RunnerHandler)
])

def pj(a):
    print(json.dumps(a))

if __name__ == "__main__":

    print("Starting EREB on http://localhost:8888")
    task_controller.start()

    t = task_controller.get_recent_history(2)

    application.listen(8888)
    IOLoop.instance().start()
