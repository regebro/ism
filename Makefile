PYTHON=$(CURDIR)/bin/python
COVERAGE=COVERAGE_FILE=$(CURDIR)/.coverage $(CURDIR)/bin/coverage
PIP=$(CURDIR)/bin/pip

all: test

bin:
	virtualenv .
	$(PIP) install -r test-requirements.txt

src/doctrine.code:
	git clone git@github.com:regebro/doctrine.code.git src/doctrine.code

src/doctrine.urwid:
	git clone git@github.com:regebro/doctrine.urwid.git src/doctrine.urwid

dependencies: src/doctrine.code src/doctrine.urwid

env: dependencies bin
	cd src/doctrine.code; $(PYTHON) setup.py develop
	cd src/doctrine.urwid; $(PYTHON) setup.py develop
	$(PYTHON) setup.py develop

test: env
#	$(PYTHON) setup.py test
	cd src/doctrine.code; $(PYTHON) setup.py test
	cd src/doctrine.urwid; $(PYTHON) setup.py test

coverage: env
	cd src/doctrine.code; $(COVERAGE) run --source=doctrine setup.py test
	cd src/doctrine.urwid; $(COVERAGE) run -a --source=doctrine setup.py test
	$(COVERAGE) html

update: dependencies
	git pull
	cd src/doctrine.code; git pull
	cd src/doctrine.urwid; git pull

status: dependencies
	git status
	cd src/doctrine.code; git status
	cd src/doctrine.urwid; git status
