from tornado.ioloop import IOLoop
from tornado import gen
import tornado.web
from lib.task_runner import TaskRunner
from lib.tasks_controller import TaskController
import time
import json

task_controller = TaskController()

class TasksHandler(tornado.web.RequestHandler):
    def get(self, task_id, action, task_run_id):
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
            elif action == 'task_runs' and task_run_id != '':
                detailed_task_run = task_controller.get_detailed_task_run_info(task_id, task_run_id)
                if not detailed_task_run:
                    self.raise_404('Task run %s/%s not found' % (task_id, task_run_id))
                else:
                    result = json.dumps(detailed_task_run)

        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(result)

    def post(self, task_id, action, task_run_id):
        result = '404'
        config = json.loads(self.request.body.decode())

        if task_id == '' and action == '':
            self.raise_404('Unknown route')
        elif task_id != '':
            is_valid_config = task_controller.validate_config(config)

            if not is_valid_config:
                self.raise_500('Cannot update task with config: %s' % json.dumps(config))
            else:
                task = task_controller.set_task_by_id(task_id, config)
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
    (r"/tasks/?([^/]*)/?([^/]*)/?([^/]*)$", TasksHandler),
    (r"/status/?(.*)$", RunnerHandler)
])

def pj(a):
    print(json.dumps(a))

if __name__ == "__main__":

    print("Starting EREB on http://localhost:8888")
    task_controller.start()

    application.listen(8888)
    IOLoop.instance().start()
