.PHONY: build

PYTHON=python3

build:
	$(PYTHON) setup.py build

clean:
	$(PYTHON) setup.py clean --all

install:
	$(PYTHON) setup.py install

docker_build:
	docker build -t aviasales/ereb --force-rm --no-cache .
