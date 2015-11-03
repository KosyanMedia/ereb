import time
import datetime
import subprocess
import urllib.parse
import logging

class Notifier():
    def __init__(self, notifier_config, output='logger'):
        self.output = output
        self.hostname = self.get_hostname()
        try:
            if output in notifier_config:
                self.cmd = notifier_config[output]
            else:
                raise Exception("Missed notifier config for %s" % output)
        except Exception as e:
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
        return subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE).stdout.read().decode().replace('\n','')
