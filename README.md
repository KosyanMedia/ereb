# Hey, it's Ereb

[![PyPI version](https://badge.fury.io/py/ereb.svg)](https://badge.fury.io/py/ereb)

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

This will install `ereb` to `/usr/local/bin/ereb`.

## For Debian/Ubuntu users

If you want to properly install ereb so that it starts on system start, make use of systemd.

1. Create a proper init script: `vim /etc/init.d/ereb`:
 ```
 #!/bin/bash
 ### BEGIN INIT INFO
 # Provides:          ereb
 # Required-Start:    $remote_fs $syslog
 # Required-Stop:     $remote_fs $syslog
 # Default-Start:     2 3 4 5
 # Default-Stop:      0 1 6
 # Short-Description: Start ereb at boot time
 # Description:       Ereb is a cool crontab with web interface.
 ### END INIT INFO

 PIDFILE=/var/run/ereb.pid

 case $1 in
    start)
        # as a detached process
        /usr/local/bin/ereb >> /var/log/ereb.log 2>&1 &
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
2. Create a systemd unit: `vim /lib/systemd/system/ereb.service`:
 ```
 [Unit]
 SourcePath=/etc/init.d/ereb
 Description=Easy installable cron with web interface

 [Service]
 Type=forking
 PIDFile=/var/run/ereb.pid
 Restart=always
 TimeoutSec=5min
 IgnoreSIGPIPE=no
 KillMode=process
 GuessMainPID=no
 RemainAfterExit=yes
 ExecStart=/etc/init.d/ereb start
 ExecStop=/etc/init.d/ereb stop
 ```
3. Place the unit under `multi-user` target:
 ```
 ln -s /lib/systemd/system/ereb.service /etc/systemd/system/multi-user.target.wants/ereb.service
 ```
4. Enable the service so that it starts on boot:
 ```
 systemctl enable ereb.service
 ```

Now you can try to `reboot` your server and make sure that `ps aux | grep ereb | grep -v grep` shows up running ereb instance.

Read more on <https://www.digitalocean.com/community/tutorials/systemd-essentials-working-with-services-units-and-the-journal>

# Config flags
```
--datadog-agent-host             host where datadog agent is running (default
                                   localhost)
--datadog-agent-port             port where datadog agent is running (default
                                   8125)
--datadog-metrics                send metrics to datadog (default False)
--datadog-tag                    value for special `ereb:%datadog_tag%` tag
                                   in datadog metrics, sent with every event
--history-dir                    directory for history storage (default ./var)
--notifier-config                notifier json config (default ./notifier.json)
--notifier-host                  host for links in notifications (default hostname)
--notify-to                      notifications channel (default logger)
--port                           port to listen on (default 8888)
--tasks-dir                      directory with tasks config files (default ./etc)
```

# Generic task run

It is possible to run generic command without creating new task.
POST requiest to `generic_tasks/run` with `name`, `cmd` and `timeout` params.
Example:
```
curl -v -X POST 'http://localhost:8888/generic_tasks/run' -d '{"name": "foo", "cmd": "echo bar", "timeout": 60 }'
```
After that in Ereb new task with name `__generic_foo` will start

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
