# coding: utf-8

import sys
import re
import os
import json
import string
import logging
import random
from tornado.options import define, options

REGEXP = r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+([^#]+)'
NAME_REGEXP = r'\/([^\/]+).(sh|py|rb)'

define(
    "output_dir", default="./etc", type=str,
    help="output directory for new tasks"
)

options.parse_command_line()


def generate_random_name():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10))


if not os.path.exists(options.output_dir):
    logging.info('Creating directory: %s' % options.output_dir)

    os.makedirs(options.output_dir)

for line in sys.stdin.readlines():
    line = line.strip()

    if len(line) > 0:
        try:
            if not line[0] == '#':
                match = re.search(REGEXP, line)

                if match:
                    match_groups = match.groups()
                    crontab = ' '.join(match_groups[:5])
                    cmd = match_groups[5]
                    script_name_match = re.search(NAME_REGEXP, cmd)
                    logging.info('Parsing: %s' % line)

                    if script_name_match:
                        task_name = script_name_match.group(1)

                        logging.info(
                            'Got task name from command: %s' % task_name)
                    else:
                        task_name = '_'.join('task', generate_random_name())

                        logging.info('Generated task name: %s' % task_name)

                    task_config = {
                        'cron_schedule': crontab,
                        'cmd': cmd,
                        'enabled': False,
                        'name': task_name
                    }

                    path = options.output_dir + '/%s.json' % task_name

                    if os.path.isfile(path):
                        task_name = '_'.join(
                            [task_name, generate_random_name()])
                        path = options.output_dir + '/%s.json' % task_name

                    f = open(options.output_dir + '/%s.json' % task_name, 'w')
                    f.write(json.dumps(task_config, sort_keys=True, indent=4))
                    f.close()

                    logging.warning('Successfully generated  %s/%s.json' % (
                        options.output_dir, task_name))

        except Exception as e:
            logging.exception('Something went wrong')
