from tornado.ioloop import IOLoop
import tornado.web
import json
import logging
from tornado import websocket
import subprocess
from functools import partial
import sys
import signal
import pkg_resources
import os

from ereb.tasks_controller import TaskController


class SocketHandler(websocket.WebSocketHandler):

    def initialize(self, task_controller, websocket_clients):
        self.task_controller = task_controller
        self.websocket_clients = websocket_clients

    def check_origin(self, origin):
        return True

    def open(self):
        self.websocket_clients.append(self)
        logging.info('WebSocket opened, clients: %s' % len(self.websocket_clients))
        self.write_message(self.task_controller.get_status())

    def on_close(self):
        self.websocket_clients.remove(self)
        logging.info('WebSocket closed, clients: %s' % len(self.websocket_clients))


class GenericTasksHandler(tornado.web.RequestHandler):

    def initialize(self, task_controller):
        self.task_controller = task_controller

    def post(self):
        params = json.loads(self.request.body.decode())
        self.task_controller.run_generic_task(params['name'], params['cmd'], params['timeout'])
        self.write('ok')


class TasksHandler(tornado.web.RequestHandler):

    def initialize(self, task_controller):
        self.task_controller = task_controller

    def get(self, task_id, action, task_run_id):
        result = '404'
        if task_id == '' and action == '':
            tasks = self.task_controller.get_task_list(with_history=True, task_run_limit=20)
            result = json.dumps(tasks)
        elif task_id != '':
            task = self.task_controller.get_task_by_id(task_id, with_extra_info=True)
            if not task:
                self.raise_404('task %s not found' % task_id)
            if action == '':
                result = json.dumps({
                    'config': task,
                    'runs': self.task_controller.get_task_runs_for_task_id(task_id)
                })
            elif action == 'run':
                self.task_controller.run_task_by_task_id(task_id)
                result = 'task_run'
            elif action == 'shutdown':
                self.task_controller.shutdown_run_for_task_id(task_id)
                result = 'task %s killed' % task_id
            elif action == 'task_runs' and task_run_id != '':
                detailed_task_run = self.task_controller.get_detailed_task_run_info(task_id, task_run_id)
                if not detailed_task_run:
                    self.raise_404('Task run %s/%s not found' % (task_id, task_run_id))
                else:
                    result = json.dumps(detailed_task_run)
            elif action == 'task_run_stdout' and task_run_id != '':
                task_run_stdout = self.task_controller.get_stdout_for_task_run_id(task_id, task_run_id)
                if not task_run_stdout:
                    self.raise_404('Stdout %s/%s not found' % (task_id, task_run_id))
                else:
                    result = task_run_stdout
            elif action == 'task_run_stderr' and task_run_id != '':
                task_run_stderr = self.task_controller.get_stderr_for_task_run_id(task_id, task_run_id)
                if not task_run_stderr:
                    self.raise_404('Stderr for %s/%s not found' % (task_id, task_run_id))
                else:
                    result = task_run_stderr

        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(result)

    def post(self, task_id, action, task_run_id):
        result = '404'
        config = json.loads(self.request.body.decode())

        if task_id == '' and action == '':
            is_valid_config = self.task_controller.validate_config(config)
            if not is_valid_config:
                self.raise_500('Cannot update task with config: %s' % json.dumps(config))
            else:
                task_id = config['task_id'].replace(' ', '_')
                task = self.task_controller.set_task_by_id(task_id, config)
                result = 'Success'
                self.set_header('Access-Control-Allow-Origin', '*')
                self.write(result)
        elif task_id != '':
            is_valid_config = self.task_controller.validate_config(config)

            if not is_valid_config:
                self.raise_500('Cannot update task with config: %s' % json.dumps(config))
            else:
                task = self.task_controller.set_task_by_id(task_id, config)
                result = 'Success'
                self.set_header('Access-Control-Allow-Origin', '*')
                self.write(result)

    def delete(self, task_id, action, task_run_id):
        result = '404'

        if task_id == '' and action == '':
            self.raise_404('Unknown route')
        elif task_id != '':
            task = self.task_controller.delete_task_by_id(task_id)
            if not task:
                self.raise_500('Cannot delete task with config: %s' % json.dumps(config))
            else:
                result = 'Success'
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(result)

    def options(self, task_id, action, task_run_id):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE')

        self.write('')

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

    def initialize(self, task_controller):
        self.task_controller = task_controller

    def get(self, cmd):
        if cmd == '':
            result = json.dumps(self.task_controller.get_status())
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write(result)
        if cmd == 'dashboard':
            result = json.dumps(self.task_controller.get_dashboard_info())
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write(result)
        if cmd == 'recent_failed_tasks':
            recent_tasks = self.task_controller.get_recent_history(100)
            failed_tasks = []
            for task in recent_tasks:
                print(task['exit_code'])
                if task['exit_code'] != 0 and task['exit_code'] != 'None':
                    failed_tasks.append(task)
            result = json.dumps(failed_tasks)
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write(result)
        elif cmd == 'start':
            self.task_controller.start_task_loop()
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write('Success')
        elif cmd == 'stop':
            self.task_controller.stop_task_loop()
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write('Success')


def shutdown(shutdown_tasks, *args):
    logging.info("shutting down...")
    shutdown_tasks()
    IOLoop.current().stop()
    sys.exit(0)


def main():
    from tornado.options import define, options
    define("port", default=8888, type=int, help="port to listen on")
    define("tasks_dir", default=os.path.dirname(os.path.realpath(__file__)) +
           "/../etc", type=str, help="directory with tasks config files")
    define("history_dir", default=os.path.dirname(os.path.realpath(__file__)) +
           "/../var", type=str, help="directory for history storage")
    define("notifier_config", default=os.path.dirname(os.path.realpath(__file__)) +
           "/../notifier.json", type=str, help="notifier json config")
    define("notify_to", default="logger", type=str, help="notifications channel")
    define("notifier_host", default="hostname", type=str, help="host for links in notifications")
    define("datadog_metrics", default=False, help="send metrics to datadog")

    tornado.options.parse_command_line()

    datadog_metrics = True if options.datadog_metrics else False
    ereb_version = version = pkg_resources.require("ereb")[0].version

    default_wi_config = """
        window.DEFAULT_CONFIG = {}
    """.format({
        'port': options.port,
        'version': ereb_version
    })

    default_wi_config_path = os.path.dirname(os.path.realpath(__file__)) + '/ereb-wi/default_config.js'

    with open(default_wi_config_path, 'w') as f:
        f.write(default_wi_config)

    try:
        with open(options.notifier_config) as notifier_config_file:
            notifier_config = json.load(notifier_config_file)
    except Exception as e:
        logging.info('You can use Slack notifier by create notifier.json')
        notifier_config = {}

    websocket_clients = []

    task_controller = TaskController(
        tasks_dir=options.tasks_dir,
        history_dir=options.history_dir,
        notifier_config=notifier_config,
        notify_to=options.notify_to,
        notifier_host=options.notifier_host,
        port=options.port,
        websocket_clients=websocket_clients,
        datadog_metrics=datadog_metrics)

    logging.info("Starting EREB on http://{}:{}".format('0.0.0.0', options.port))
    if datadog_metrics:
        logging.info("Sending metrics to Datadog enabled")

    task_controller.start()

    application = tornado.web.Application([
        (r"/tasks/?([^/]*)/?([^/]*)/?([^/]*)$", TasksHandler, dict(task_controller=task_controller)),
        (r"/generic_tasks/run", GenericTasksHandler, dict(task_controller=task_controller)),
        (r"/status/?(.*)$", RunnerHandler, dict(task_controller=task_controller)),
        (r'/ws', SocketHandler, dict(task_controller=task_controller, websocket_clients=websocket_clients)),
        (r"/(.*)", tornado.web.StaticFileHandler,
         {"path": os.path.dirname(os.path.realpath(__file__)) + "/ereb-wi", "default_filename": "index.html"})
    ], gzip=True)

    signal.signal(signal.SIGTERM, partial(shutdown, task_controller.shutdown_tasks))
    signal.signal(signal.SIGHUP, partial(shutdown, task_controller.shutdown_tasks))
    signal.signal(signal.SIGINT, partial(shutdown, task_controller.shutdown_tasks))

    application.listen(options.port)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
