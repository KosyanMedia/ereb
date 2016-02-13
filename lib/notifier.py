import subprocess
import urllib.parse
import logging


class Notifier():
    def __init__(self, notifier_config, notify_to='logger', websocket_clients=[], port=8888):
        self.notify_to = notify_to
        self.hostname = self.get_hostname()
        self.port = port
        self.websocket_clients = websocket_clients
        try:
            if notify_to in notifier_config:
                self.cmd = notifier_config[notify_to]
        except:
            logging.exception("Notifier error:")
            self.cmd = None

    def error(self, link, message):
        if self.cmd:
            if "http" in self.cmd:
                link = urllib.parse.quote(link)
                message = urllib.parse.quote(message)

            notifier_cmd = self.cmd.replace('%s', "{0}\n{1}".format(link, message))
            subprocess.Popen(notifier_cmd, shell=True, stdout=subprocess.PIPE)
        else:
            logging.warning("Notifications are turned off")

    def send_failed_task_run(self, task_run):
        link = "{0}:{1}/#/tasks/{2}/runs/{3}".format(self.hostname, self.port, task_run.task_id, task_run.id)
        message = "Task {0} failed".format(task_run.task_id)
        self.error(link, message)

    def get_hostname(self):
        return subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE).stdout.read().decode().replace('\n', '')

    def websocket_send_status(self, message):
        logging.info('websocket_send_status')
        for client in self.websocket_clients:
            client.write_message(message)
