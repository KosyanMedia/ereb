import os
import json
import glob
import re
import logging
import shutil


class FileHistoryStorage():

    def __init__(self, storage_dir="./var"):
        self.storage_dir = storage_dir

    def get_recent_history(self, limit):
        task_run_files = glob.glob(self.storage_dir + '/*/*/*/state')
        result = []

        sorted_task_runs = sorted(task_run_files, key=lambda k: k.split('/')[-2], reverse=True)[:limit]

        for f in sorted_task_runs:
            with open(f) as task_run_file:
                try:
                    state = json.load(task_run_file)
                except:
                    logging.exception('Error reading state json')
                    continue
            result.append(state)
        return result

    def get_currently_running_tasks(self):
        current_runs = glob.glob(self.storage_dir + '/*/current')
        result = []
        for f in current_runs:
            with open(f) as current_run_file:
                file_path = current_run_file.read()

            with open(file_path + '/state') as task_run_file:
                running_task = json.load(task_run_file)

            result.append(running_task)

        return result

    def get_last_day_for_task_id(self, task_id):
        days = list(map(lambda x: x.split('/')[-1], glob.glob(self.storage_dir + '/%s/*' % task_id)))
        days.sort(reverse=True)
        if len(days) == 0:
            return None
        last_day = days.pop(0)
        if last_day == 'current':
            last_day = days.pop(0)
        return last_day

    def get_task_runs_for_task_id(self, task_id, limit=20):
        last_day = self.get_last_day_for_task_id(task_id)
        if not last_day:
            return []

        all_task_run_files = glob.glob(self.storage_dir + '/%s/%s/*/state' % (task_id, last_day))
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
        return result

    def get_detailed_history_for_task_id(self, task_id, limit=20):
        last_day = self.get_last_day_for_task_id(task_id)
        if not last_day:
            return []

        task_run_dirs = glob.glob(self.storage_dir + '/%s/%s/*' % (task_id, last_day))
        task_run_dirs.sort(reverse=True)
        limited_task_run_dirs = task_run_dirs[:limit]

        result = []
        for f in task_run_dirs:
            if not os.path.isfile(f + '/state'):
                break

            task_run = {}

            with open(f + '/state') as file_content:
                try:
                    task_run['state'] = json.load(file_content)
                except Exception as e:
                    logging.exception('Error reading state json')
                    continue
            for x in ['stdout', 'stderr']:
                filename = '/'.join([f, x])
                if os.path.isfile(filename):
                    with open(f + '/' + x) as file_content:
                        task_run[x] = file_content.read()
                else:
                    task_run[x] = 'Empty'
            result.append(task_run)

        return result

    def get_detailed_task_run_info(self, task_id, task_run_id):
        day = task_run_id[:10]
        task_run_path = self.storage_dir + '/%s/%s/%s' % (task_id, day, task_run_id)

        task_run = {}
        with open(task_run_path + '/state') as file_content:
            task_run['state'] = json.load(file_content)
        for x in ['stdout', 'stderr']:
            file_path = '/'.join([task_run_path, x])
            if os.path.isfile(file_path):
                with open(task_run_path + '/' + x) as file_content:
                    task_run[x] = file_content.read()
            else:
                task_run[x] = ''

        return task_run

    def finalize_task_run(self, task_run):
        task_run.finalize()
        task_run.state['exit_code'] = '-1'
        self.update_state_for_task_run(task_run)
        self.delete_current_task_run_for_task(task_run)

    def get_task_run_path(self, task_run):
        return '/'.join([
            self.storage_dir,
            task_run.task_id,
            task_run.state['day_of_start'],
            task_run.id
        ])

    def update_state_for_task_run(self, task_run):
        state_file_path = self.get_task_run_path(task_run) + '/state'
        self.write_to_file(state_file_path, json.dumps(task_run.state))

    def update_stdout_for_task_run_id(self, task_run):
        stdout_file_path = self.get_task_run_path(task_run) + '/stdout'
        self.write_to_file(stdout_file_path, task_run.stdout)

    def update_stderr_for_task_run_id(self, task_run):
        stderr_file_path = self.get_task_run_path(task_run) + '/stderr'
        self.write_to_file(stderr_file_path, task_run.stderr)

    def update_current_task_run_for_task(self, task_run):
        file_path = '/'.join([self.storage_dir, task_run.task_id, 'current'])
        self.write_to_file(file_path, self.get_task_run_path(task_run))

    def delete_current_task_run_for_task(self, task_run):
        file_path = '/'.join([self.storage_dir, task_run.task_id, 'current'])
        if os.path.isfile(file_path):
            os.remove(file_path)

    def task_valid_to_run(self, task_id):
        file_path = '/'.join([self.storage_dir, task_id, 'current'])
        return not os.path.isfile(file_path)

    def prepare_task_run(self, task_run):
        task_path = '/'.join([self.storage_dir, task_run.task_id])
        task_path = self.get_task_run_path(task_run)
        if not os.path.isdir(task_path):
            os.makedirs(task_path)
        self.remove_old_day_dirs(task_run)

    def remove_old_day_dirs(self, task_run, days_limit=1):
        day_dirs = glob.glob(self.storage_dir + '/' + task_run.task_id + '/*')
        if len(day_dirs) > days_limit:
            day_dirs.sort()
            last_day = day_dirs[0]
            shutil.rmtree(last_day)

    def write_to_file(self, path, content):
        with open(path, 'w') as f:
            f.write(content)
