# Hey, it's Ereb

Basically, it's easy installable cron with web interface. Just `pip3 install ereb && ereb` and open `localhost:8888`
Ereb is *not* based on system crond, it works with own scheduler written using Tornado.
It has:
- JSON API
- stderr, stdout of each task run
- historical data about slowest and most failing tasks
- no memory leaks (hope so, but uptime >months without memory leak is normal)
- crond syntax
- Slack notifications
- Tyler The Creator as a logo

![ereb](https://cloud.githubusercontent.com/assets/1700932/21672416/0a92d7c0-d355-11e6-9fd2-4ce8ca31aabc.png)

And the best thing about ereb: it really works and made already thousands task runs on our servers.

# How to install

Under `root`:
```
pip3 install ereb
```

*Note: This will install `ereb` to `/usr/local/bin/ereb`.*

# JSON api

get `/status` => info about next runs
get `/tasks` => tasks list
get `/tasks/foo` => extended info about *foo* task with recent task runs
post `/tasks/foo` => update *foo* task config
get `/tasks/foo/task_runs/%id%` => get task run %id% info for *foo* task
get `/tasks/foo/run` => manual run of *foo* task
get `/tasks/foo/shutdown` => kill currenly running *foo* task

# Development

## Backend development
First you do
`pip3 install -r requirements.txt`

then

`python3 ereb/erebd.py`

# UI development

For js app building you need webpack (and nodejs of course)
You can use webpack-dev-server, so
```
cd ereb/ereb-wi
npm install
npm install -g webpack
npm install -g webpack-dev-server

webpack-dev-server
```

And your live-reloadable app will be served on `localhost:8080`

After work done, you have to make production build with
`cd ereb/ereb-wi && webpack -p`
and commit changes to repo :)

## Migration from  crontab

Use utility crontab_converter.py

```
crontan -l | python3 crontab_converter.py --output_dir=./etc
```

to generate tasks from your crontab file.
**Important!** Check new tasks after that!

## Task config example

```json
{
  "cmd": "while :; do echo 'Hit CTRL+C'; sleep 1; done",
  "cron_schedule": "* * * * *",
  "description": "",
  "enabled": true,
  "group": "",
  "timeout": 10,
  "name": "infinite_loop",
  "shell_scripts": [],
  "task_id": "infinite_loop"
}
```

## Notifications

To turn on notifications
```sh
cp notifier.json.example notifier.json
```
and make proper shell commands.
Token ```%s``` in config will be replaced with your real error message.

Then use *--notify-to* parameter for running ereb.py, for example to use slack do:
```sh
python3 ereb.py --notify-to=slack
```

## Clean history

```sh
rm -rf var/
```

## Monit

Example monit config (for ereb installed via pip)

```
check process ereb pidfile /var/run/ereb/ereb.pid
    start program = "/etc/init.d/ereb start"
    stop program = "/etc/init.d/ereb stop"
    group system
```
Don't forget to create `/etc/init.d/ereb`:
```
#!/bin/bash

PIDFILE=/var/run/ereb/ereb.pid

case $1 in
   start)
       # as a detached process
       /usr/local/bin/ereb >> /var/log/ereb/ereb.log 2>&1 &
       # Get its PID and store it
       echo $! > ${PIDFILE}
   ;;
   stop)
      kill `cat ${PIDFILE}`
      # Now that it's killed, don't forget to remove the PID file
      rm ${PIDFILE}
   ;;
   *)
      echo "usage: ereb {start|stop}" ;;
esac
exit 0
```
And ofcourse, don't forget to
```
mkdir /var/run/ereb
mkdir /var/log/ereb
```
*Note: Now you can see `ereb` log in `/var/log/ereb/ereb.log`.*

## Troubleshooting

### My web interface stopped responding

This may happen if you have a big number of tasks and/or their schedule is quite frequent.
In this case history storage's `task_runs` table (we have `sqlite3` database) gets pretty big
after a while and causes `task scheduler` component to block the web interface's i/o loop.

There is an [issue](https://github.com/KosyanMedia/ereb/issues/41) already opened up about this
problem, but until it is resolved you can try cleaning up your `task_runs` table.

To clean up all history data for task runs older than a month, simply log into `sqlite3` (assuming
your database file has a standard `var/ereb.db` location):

```
sqlite3 var/ereb.db
```
and run a `DELETE` command:
```
DELETE FROM task_runs WHERE started_at < datetime('now', '-1 month');
```
