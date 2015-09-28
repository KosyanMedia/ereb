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
Then use *--notify-to* parameter for running ereb.py

## HTTP API

http://localhost:8888/runner
http://localhost:8888/tasks
http://localhost:8888/tasks/:task_id

## Clean history

```
rm -rf var/
```

## Web interface

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
To make production build just
```
webpack -p
```
and look to *./build* folder
