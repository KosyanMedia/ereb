from tornado.ioloop import IOLoop
from tornado import gen
import tornado.web
from lib.task_runner import TaskRunner
from lib.tasks_controller import TaskController
import time

class TasksHandler(tornado.web.RequestHandler):
    def get(self, route):
        result = '404'
        if route == 'start':
            result = self.tasks_loop_start()
        elif route == 'stop':
            result = self.tasks_loop_stop()
        elif route == 'status':
            result = self.tasks_status()
        self.write(result)

    def tasks_loop_start(self):
        task_controller.start_task_loop()
        return "started"

    def tasks_loop_stop(self):
        task_controller.stop_task_loop()
        return "stopped"

    def tasks_status(self):
        return task_controller.get_status()

task_controller = TaskController()

application = tornado.web.Application([
    (r"/tasks/(.+?)$", TasksHandler),
])

if __name__ == "__main__":

    task_controller.start()
    application.listen(8888)

    IOLoop.instance().start()
