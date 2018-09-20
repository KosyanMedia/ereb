## How to upload to pip

```
rm -rf ./dist && mkdir dist
python3 setup.py sdist
twine upload dist/*
```
