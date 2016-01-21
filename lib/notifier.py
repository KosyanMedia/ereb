import subprocess
import urllib.parse
import logging


class Notifier():
    def __init__(self, notifier_config, notify_to='logger', websocket_clients=[]):
        self.notify_to = notify_to
        self.hostname = self.get_hostname()
        self.websocket_clients = websocket_clients
        try:
            if notify_to in notifier_config:
                self.cmd = notifier_config[notify_to]
        except:
            logging.exception("Notifier error:")
            self.cmd = None

    def error(self, message):
        if self.cmd:
            if "http" in self.cmd:
                message = urllib.parse.quote(message)

            message = 'Host: {0}\n{1}'.format(self.hostname, message)

            subprocess.Popen(self.cmd % message, shell=True, stdout=subprocess.PIPE)
        else:
            logging.warning("Notifications are turned off")

    def get_hostname(self):
        return subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE).stdout.read().decode().replace('\n', '')

    def websocket_send_status(self, message):
        logging.info('websocket_send_status')
        for client in self.websocket_clients:
            client.write_message(message)
