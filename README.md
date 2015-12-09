## How to

```
pip3 install -r requirements.txt
python3 ereb.py
```

## Notifications

To turn on notifications
```
cp notifier.json.example notifier.json
```
and make proper shell commands.
Then use *--notify-to* parameter for running ereb.py, for example to use slack do:
```
python3 ereb.py --notify-to=slack
```

## Clean history

```
rm -rf var/
```

## Web interface

### Development
It's webpack based app
so, first make
```
cd ./ereb-wi
npm install
```

For development mode:
```
webpack-dev-server
```
Don't to make production build after. Just
```
webpack -p
```
and look to *./build* folder

### Production

ereb-wi is served by tornado by default at */* route

### Monit

Example monit config

```
check process ereb pidfile /PATH/TO/EREB/tmp/ereb.pid
    start program = "/bin/bash -c 'cd /PATH/TO/EREB && (python3.4 ereb.py --log_file_prefix=./tmp/ereb.log & echo $! > /PATH/TO/EREB/tmp/ereb.pid)'"
    stop program = "/bin/bash -c '/bin/kill `cat /PATH/TO/EREB/tmp/ereb.pid`'" with timeout 65 seconds
    group system
```
