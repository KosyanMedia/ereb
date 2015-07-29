## How to

```
pip3 install -r requirements.txt
python3 ereb.py
```

## Routes

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
webpack
```
and look to *./build* folder
