import subprocess
import urllib.parse
import logging
import requests
class Notifier():
    def __init__(self, notifier_config, notify_to='logger', websocket_clients=[], host='hostname', port=8888):
        self.notify_to = notify_to
        if host == 'hostname':
            self.hostname = self.get_hostname()
        else:
            self.hostname = host
        self.port = port
        self.websocket_clients = websocket_clients
        try:
            if notify_to in notifier_config:
                self.cmd = notifier_config[notify_to]
            else:
                self.cmd = None
        except:
            logging.exception("Notifier error:")
            self.cmd = None

    def error(self, link, message, task_run):
        if self.cmd:
            if self.notify_to.startswith('slack_api'):
                info =  task_run.log_info(lines_count=self.cmd.get('include_strings', 2))
                slack_payload = {
                        'attachments': [{
                            'pretext': 'Failed task',
                            'title': info['task_id'],
                            'title_link': link,
                            'text': self.cmd.get('text', 'Failed task {task_id}').format(**info),
                            'fallback': message,
                            'short': True,
                            'color': 'danger',
                            'mrkdwn_in': ['text', 'pretext']
                        }]
                    }
                channel = self.cmd.get('channel', False)
                if channel:
                    slack_payload['channel'] = channel
                response = requests.post(self.cmd['webhook_url'], json=slack_payload)
                if response.status_code != 200:
                    logging.error('Notifications Slack API error: %s' % response.text)
            else:
                if "http" in self.cmd:
                    link = urllib.parse.quote(link)
                    message = urllib.parse.quote(message)

                notifier_cmd = self.cmd.replace('%s', "{0}\n{1}".format(link, message))
                subprocess.Popen(notifier_cmd, shell=True, stdout=subprocess.PIPE)
        else:
            logging.warning("Notifications are turned off")

    def send_failed_task_run(self, task_run):
        link = "http://{0}:{1}/#/tasks/{2}/runs/{3}".format(self.hostname, self.port, task_run.task_id, task_run.id)
        message = "Task {0} failed".format(task_run.task_id)
        self.error(link, message, task_run)

    def get_hostname(self):
        return subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE).stdout.read().decode().replace('\n', '')

    def websocket_send_status(self, message):
        if len(self.websocket_clients) > 0:
            logging.info('websocket_send_status')
            for client in self.websocket_clients:
                client.write_message(message)
