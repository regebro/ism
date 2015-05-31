PYTHON=$(CURDIR)/bin/python


all: test

bin:
	virtualenv .

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
