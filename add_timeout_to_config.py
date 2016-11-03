import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config_name", help="Task config in json")
parser.add_argument("task_timeout", help="In seconds", type=int)
args = parser.parse_args()

f = open(args.config_name, 'r')
task_config = json.load(f)
if isinstance(task_config, list):
    for config in task_config:
        config['timeout'] = args.task_timeout
else:
    if isinstance(list(task_config.values())[0], dict):
        for config in task_config.values():
            config['timeout'] = args.task_timeout
    else:
        task_config['timeout'] = args.task_timeout
f.close()
f = open(args.config_name, 'r+')
json.dump(task_config, f, sort_keys=True, indent=2)
print(json.dumps(task_config, sort_keys=True, indent=2))
