import os
import glob
import logging
import shutil
import sqlite3
import time


class FusionHistoryStorage():
    # Fusion means both file (stdout and stderr) and sqlite storage
    STDOUT_LINES_LIMIT = 50

    CREATE_TABLES_SQL = ['''
        CREATE TABLE IF NOT EXISTS TASK_RUNS
            (   task_run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                task_id TEXT,
                pid INTEGER,
                exit_code INTEGER );''',
                         "CREATE INDEX IF NOT EXISTS task_id ON task_runs (task_id);",
                         "CREATE INDEX IF NOT EXISTS started_at ON task_runs (started_at);",
                         "CREATE INDEX IF NOT EXISTS task_id_started_at ON task_runs (task_id, started_at);",
                         "CREATE INDEX IF NOT EXISTS finished_at ON task_runs (finished_at);",
                         "CREATE INDEX IF NOT EXISTS started_at_exit_code ON task_runs (started_at, exit_code);"
                         ]

    COLUMNS = ['task_run_id', 'started_at', 'finished_at', 'task_id',
               'pid', 'exit_code']

    def __init__(self, storage_dir="./var"):
        self.storage_dir = storage_dir
        if not os.path.isdir(self.storage_dir):
            os.makedirs(self.storage_dir)
        self.sqlite_connection = sqlite3.connect(self.storage_dir + '/ereb.db')
        logging.info('FusionHistoryStorage => Database connected')
        for sql in self.CREATE_TABLES_SQL:
            self.sqlite_connection.execute(sql)
        logging.info('FusionHistoryStorage => Tables created')

    def get_recent_failed_task_runs(self, limit):
        columns = ['task_id', 'task_run_id', 'started_at', 'duration']
        result = self.select_to_dict('''
            select task_id, task_run_id, started_at,
                strftime('%s', finished_at) - strftime('%s', started_at) as duration
            from task_runs
            where exit_code != 0
            and finished_at != 'None'
            and started_at > datetime('now', '-1 month')
            order by started_at desc
            limit {}
        '''.format(limit), columns)

        return result

    def get_currently_running_tasks(self):
        result = self.select_to_dict('''
            select *
            from task_runs
            where finished_at = 'None'
        ''')

        return result

    def get_last_day_for_task_id(self, task_id):
        result = self.select_to_dict('''
            select *
            from task_runs
            where task_id = '%s'
            order by task_run_id desc
            limit 1
        ''' % task_id)

        if len(result) > 0:
            last_day = result[0]['started_at'][:10]
        else:
            last_day = None

        return last_day

    def get_task_runs_for_task_id(self, task_id, limit=20):
        result = self.select_to_dict('''
            select *
            from task_runs
            where task_id = '%s'
            order by task_run_id desc
            limit %s
        ''' % (task_id, limit))
        return result

    def get_task_stats_for_dashboard(self):
        columns = ['task_id', 'duration_avg', 'fails']
        start_time = time.time()
        failed_tasks = self.select_to_dict('''
        select
            task_id,
            round(avg(strftime('%s', finished_at) - strftime('%s', started_at)), 2) as duration_avg,
            sum(case when exit_code != 0 then 1 else 0 end) as fails

        from task_runs
            where started_at > datetime('now', '-1 day')
            group by task_id
            order by duration_avg desc;
        ''', columns)

        logging.warning('FusionHistoryStorage :: get_task_stats_for_dashboard sql time %s', time.time() - start_time)
        # Sqlite3 is single threaded in it takes fucking LONG time to execute 4 queries one by one
        # that's why
        # this query is ugly, single and works 4x time faster than previous

        result = {}
        result['slow_tasks'] = failed_tasks[:5]
        result['failed_tasks'] = sorted(failed_tasks, key=lambda x: x['fails'], reverse=True)[:5]

        return result

    def get_task_list_stats(self):
        columns = ['task_id', 'duration_avg', 'duration_min', 'duration_max',
                   'success', 'error', 'exit_codes']
        task_stats = self.select_to_dict('''
            select  task_id,
            round(avg(strftime('%s', finished_at) - strftime('%s', started_at)), 2) as duration_avg,
            min(strftime('%s', finished_at) - strftime('%s', started_at)) as duration_min,
            max(strftime('%s', finished_at) - strftime('%s', started_at)) as duration_max,
            sum(case when exit_code = 0 then 1 else 0 end) as success,
            sum(case when exit_code != 0 then 1 else 0 end) as error,
            group_concat(exit_code) as exit_codes
            from task_runs
            where started_at > datetime('now', '-1 day')
            group by task_id
        ''', columns)

        stats_by_task_id = {}
        for task in task_stats:
            if task['exit_codes'] != '':
                task['exit_codes'] = str(task['exit_codes']).split(',')[-self.STDOUT_LINES_LIMIT:]
            else:
                task.pop('exit_codes')

            stats_by_task_id[task['task_id']] = task

        return stats_by_task_id

    def get_detailed_task_run_info(self, task_id, task_run_id, content_size_limit=True):
        task_run = {}
        task_run['state'] = self.select_to_dict('''
            select *
            from task_runs
            where task_run_id = '%s'
        ''' % task_run_id)[0]

        day = task_run['state']['started_at'][:10]
        task_run_path = self.storage_dir + '/%s/%s/%s' % (task_id, day, task_run_id)

        for x in ['stdout', 'stderr']:
            file_path = '/'.join([task_run_path, x])
            if os.path.isfile(file_path):
                with open(task_run_path + '/' + x) as file_content:
                    lines = file_content.read().split("\n")
                    if content_size_limit:
                        task_run[x] = "\n".join(lines[-50:])
                    else:
                        task_run[x] = "\n".join(lines)
            else:
                task_run[x] = ''

        return task_run

    def finalize_task_run(self, task_run):
        task_run.finalize()
        task_run.state['exit_code'] = '-1'
        self.update_state_for_task_run(task_run)

    def get_task_run_path(self, task_run):
        print(task_run.id)
        return '/'.join([
            self.storage_dir,
            task_run.task_id,
            task_run.state['started_at'][:10],
            task_run.id
        ])

    def update_state_for_task_run(self, task_run):
        self.sqlite_connection.execute('''
            update task_runs
            set started_at = '%s',
                finished_at = '%s',
                task_id = '%s',
                pid = '%s',
                exit_code = '%s'
            where task_run_id = '%s';''' % (
            task_run.state['started_at'], task_run.state['finished_at'],
            task_run.state['task_id'], task_run.state['pid'],
            task_run.state['exit_code'], task_run.id))
        self.sqlite_connection.commit()
        logging.warn('FusionHistoryStorage updated!')

    def update_stdout_for_task_run_id(self, task_run):
        stdout_file_path = self.get_task_run_path(task_run) + '/stdout'
        self.write_to_file(stdout_file_path, task_run.stdout)

    def update_stderr_for_task_run_id(self, task_run):
        stderr_file_path = self.get_task_run_path(task_run) + '/stderr'
        self.write_to_file(stderr_file_path, task_run.stderr)

    def task_valid_to_run(self, task_id):
        currently_running = self.select_to_dict('''
            select *
            from task_runs
            where task_id = '%s' and finished_at = 'None'
        ''' % task_id)
        return len(currently_running) == 0

    def prepare_task_run(self, task_run):
        self.sqlite_connection.execute('''
            insert into task_runs(task_id, started_at)
            values ('%s', '%s');
        ''' % (task_run.task_id, task_run.state['started_at']))
        self.sqlite_connection.commit()

        task_run_id = str(list(self.sqlite_connection.execute('select last_insert_rowid();'))[0][0])

        task_run.id = task_run_id

        task_path = '/'.join([self.storage_dir, task_run.task_id])
        task_path = self.get_task_run_path(task_run)
        if not os.path.isdir(task_path):
            os.makedirs(task_path)
        self.remove_old_history_for_task_id(task_run.task_id, days_limit=30)

    def remove_old_history_for_task_id(self, task_id, days_limit=30):
        day_dirs = glob.glob(self.storage_dir + '/' + task_id + '/*')
        if len(day_dirs) > days_limit:
            day_dirs.sort()
            last_day = day_dirs[0]
            shutil.rmtree(last_day)
        self.sqlite_connection.execute('''
            delete from task_runs
            where task_id = '%s' and started_at < datetime('now', '-%d days');
        ''' % (task_id, days_limit))
        self.sqlite_connection.commit()

    def select_to_dict(self, sql, columns=COLUMNS):
        cursor = self.sqlite_connection.execute(sql)
        result = []

        for row in cursor:
            r = {}
            for i, column in enumerate(columns):
                r[column] = row[i]
            result.append(r)

        return result

    def write_to_file(self, path, content):
        with open(path, 'w') as f:
            f.write(content)
