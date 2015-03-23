import tornado.ioloop
import tornado.web
from lib.task_runner import TaskRunner
from lib.tasks_controller import TaskController

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, ereb")


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":

    task_controller = TaskController()
    task_controller.loop()

    # application.listen(8888)
    # tornado.ioloop.IOLoop.instance().start()
