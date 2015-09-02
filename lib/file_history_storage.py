# 4 interfaces for HistoryStorage:
#
# get_recent_history
# get_task_runs_for_task_id
# get_detailed_history_for_task_id
# get_detailed_task_run_info

import os
import sys
import json
import glob
import re
import logging
import time

class FileHistoryStorage():
    def __init__(self, storage_dir="./var"):
        self.storage_dir = storage_dir

    def get_recent_history(self, limit):
        task_run_files = glob.glob(self.storage_dir + '/*/*/state')
        result = []
        regexp = re.compile('./[^/]+/([^/]+)/([^/]+)/state', re.IGNORECASE)
        for f in task_run_files:
            matched = regexp.search(f)
            task_id, task_run_id = matched.group(1), matched.group(2)

            with open(f) as task_run_file:
                state = json.load(task_run_file)
            state['task_id'], state['task_run_id'] = task_id, task_run_id
            result.append(state)

        return sorted(result, key=lambda k: k['started_at'], reverse=True)[:limit]

    def get_task_runs_for_task_id(self, task_id, limit=20):
        all_task_run_files = glob.glob(self.storage_dir + '/%s/*/state' % task_id)
        all_task_run_files.sort(reverse=True)
        limited_task_run_files = all_task_run_files[:limit]

        result = []
        regexp = re.compile('./[^/]+/[^/]+/([^/]+)/state', re.IGNORECASE)
        for f in limited_task_run_files:
            task_run_id = regexp.search(f).group(1)
            with open(f) as task_run_file:
                task_run = json.load(task_run_file)
                task_run['id'] = task_run_id
                result.append(task_run)
        return sorted(result, key=lambda k: k['started_at'], reverse=True)[:limit]


    def get_detailed_history_for_task_id(self, task_id, limit=20):
        task_run_dirs = glob.glob(self.storage_dir + '/%s/*' % task_id)
        result = []
        regexp = re.compile('./[^/]+/[^/]+/([^/]+)$', re.IGNORECASE)
        for f in task_run_dirs:
            if not os.path.isfile(f + '/state'):
                break

            task_run_id = regexp.search(f).group(1)
            task_run = {
                'id': task_run_id
            }

            with open(f + '/state') as file_content:
                task_run['state'] = json.load(file_content)
            for x in ['stdout', 'stderr', 'pid']:
                filename = '/'.join([f, x])
                if os.path.isfile(filename):
                    with open(f + '/' + x) as file_content:
                        task_run[x] = file_content.read()
                else:
                    task_run[x] = 'Empty'
            result.append(task_run)

        return sorted(result, key=lambda k: k['state']['started_at'], reverse=True)[:limit]

    def get_detailed_task_run_info(self, task_id, task_run_id):
        task_run_dirs = glob.glob(self.storage_dir + '/%s/%s' % (task_id, task_run_id))

        if len(task_run_dirs) == 0:
            return None

        task_run_dir = task_run_dirs[0]
        task_run = {
            'id': task_run_id
        }

        with open(task_run_dir + '/state') as file_content:
            task_run['state'] = json.load(file_content)
        for x in ['stdout', 'stderr', 'pid']:
            with open(task_run_dir + '/' + x) as file_content:
                task_run[x] = file_content.read()

        return task_run


    def update_state_for_task_run_id(self, task_id, task_run_id, state):
        state_file_path = '/'.join([self.storage_dir, task_id, task_run_id, 'state'])
        self.write_to_file(state_file_path, json.dumps(state))

    def update_pid_for_task_run_id(self, task_id, task_run_id, pid):
        pid_file_path = '/'.join([self.storage_dir, task_id, task_run_id, 'pid'])
        self.write_to_file(pid_file_path, pid)

    def update_stdout_for_task_run_id(self, task_id, task_run_id, stdout):
        stdout_file_path = '/'.join([self.storage_dir, task_id, task_run_id, 'stdout'])
        self.write_to_file(stdout_file_path, stdout)

    def update_stderr_for_task_run_id(self, task_id, task_run_id, stderr):
        stderr_file_path = '/'.join([self.storage_dir, task_id, task_run_id, 'stderr'])
        self.write_to_file(stderr_file_path, stderr)

    def update_current_task_run_for_task(self, task_id, task_run_id):
        file_path = '/'.join([self.storage_dir, task_id, 'current'])
        self.write_to_file(file_path, task_run_id)

    def delete_current_task_run_for_task(self, task_id):
        file_path = '/'.join([self.storage_dir, task_id, 'current'])
        if os.path.isfile(file_path):
            os.remove(file_path)

    def task_valid_to_run(self, task_id):
        file_path = '/'.join([self.storage_dir, task_id, 'current'])
        return not os.path.isfile(file_path)

    def prepare_task_run(self, task_id, task_run_id):
        task_path = '/'.join([self.storage_dir, task_id])
        if not os.path.isdir(task_path):
            os.makedirs(task_path)
        current_run_path = '/'.join([task_path, task_run_id])
        if not os.path.isdir(current_run_path):
            os.makedirs(current_run_path)

    def write_to_file(self, path, content):
        with open(path, 'w') as f:
            f.write(content)
