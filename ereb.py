import tornado.ioloop
import tornado.web
import os
import time
import datetime
import sys
import subprocess
import json
import glob
import re
from crontab import CronTab
import pprint

pp = pprint.PrettyPrinter(indent=4)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, ereb")

class TaskController():
    def __init__(self):
        self.tasks_list = {}
        self.update_config()

    def update_config(self):
        new_config = self.get_tasks_config()
        result = new_config != self.tasks_list
        self.tasks_list = new_config
        return result

    def loop(self):
        while 1:
            if self.update_config():
                print("Config changed!")
            tasks_by_schedule = {}
            now = time.time()
            for task in self.tasks_list:
                next = CronTab(task['cron_schedule']).next(now)
                if next in tasks_by_schedule:
                    tasks_by_schedule[next].append(task)
                else:
                    tasks_by_schedule[next] = [task]

            next_tasks_with_crontab = sorted(tasks_by_schedule.items(), key=lambda x: x[0] )[0]
            next_run = next_tasks_with_crontab[0]
            next_tasks = next_tasks_with_crontab[1]
            print('Next run in %s seconds' % str(next_run))
            print('From process with pid %s' % os.getpid())
            time.sleep(next_run)
            print('Now running %s tasks' % len(next_tasks))
            pp.pprint(next_tasks)
            for task in next_tasks:
                print('Running %s task' % task['name'])
                TaskRunner(task['name']).run_task(task['cmd'])

    def get_tasks_config(self):
        regexp = re.compile('.+\/(.+).json', re.IGNORECASE)
        re.search('.+\/(.+).json', './etc/foo.json').groups(0)[0]
        config = []
        for f in glob.glob('./etc/*.json'):
            task_name = regexp.search(f).group(1)
            with open(f) as config_file:
                c = json.load(config_file)
            c['name'] = task_name
            config.append(c)
        return config

class TaskRunner():
    def __init__(self, taskname):
        self.taskname = taskname
        self.state = {}

    def get_human_readable_timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S_%f')

    def get_timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    def get_state_as_json(self):
        return json.dumps(self.state)

    def to_file(self, path, str):
        with open(path, 'w') as f:
            f.write(str)

    def run_task(self, cmd):
        print("Runner started, %s" % self.taskname)
        print("Command: %s" % cmd)

        timestamp = self.get_human_readable_timestamp()

        task_path = './var/' + self.taskname
        if not os.path.isdir(task_path):
            os.makedirs(task_path)
        current_run_path = task_path + '/' + timestamp
        if not os.path.isdir(current_run_path):
            os.makedirs(current_run_path)

        new_pid = os.fork()
        if not new_pid  == 0:
            self.to_file(current_run_path + '/pid', str(new_pid))
        else:
            stdout = open(current_run_path + '/stdout', 'w')
            stderr = open(current_run_path + '/stderr', 'w')
            self.state['current'] = 'running'
            self.state['started_at'] = self.get_timestamp()
            self.to_file(current_run_path + '/state', self.get_state_as_json())
            self.to_file(task_path + '/current', timestamp)
            self.state['exit_code'] = subprocess.call(cmd, stdout=stdout, stderr=stderr, shell=True)
            self.state['finished_at'] = self.get_timestamp()
            self.state['current'] = 'finished'
            self.to_file(current_run_path + '/state', self.get_state_as_json())
            os.remove(task_path + '/current')
            sys.exit()

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":

    task_controller = TaskController()
    task_controller.loop()

    # application.listen(8888)
    # tornado.ioloop.IOLoop.instance().start()
