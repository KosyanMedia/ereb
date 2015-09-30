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
