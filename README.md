## How to

First off, you need fresh node and npm. Go to [nodejs.org](nodejs.org) and follow installation instructions.
Also you need python3. Assuming you have [brew](http://brew.sh/),
```sh
brew install python3
pip3 install -r requirements.txt
python3 ereb.py
```

## Migration from  crontab

Use utility crontab_converter.py

```
crontan -l | python3 crontab_converter.py --output_dir=./etc
```

to generate tasks from your crontab file.
**Important!** Check new tasks after that!


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

## Web interface

### Development
It's webpack based app
so, first make
```sh
cd ./ereb-wi
npm install
```

For development mode:
```sh
webpack-dev-server
```
Don't to make production build after. Just
```sh
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
w
