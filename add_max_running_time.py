import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config_name", help="Task config in json")
parser.add_argument("max_running_hours", help="In hours", type=int)
args = parser.parse_args()

f = open(args.config_name, 'r')
task_config = json.loads(f.read())
if isinstance(task_config, list):
    for config in task_config:
        config['max_running_time_hours'] = args.max_running_hours
else:
    task_config['max_running_time_hours'] = args.max_running_hours
f.close()
f = open(args.config_name, 'r+')
json.dump(task_config, f)
print(task_config)
