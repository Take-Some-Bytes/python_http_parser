# Shortcuts for running utility commands.

ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname)  # same as "uname -s"
endif

ifeq ($(DETECTED_OS),Windows)
    SHELL := powershell.exe
endif

clean-build:
# These check for the existence of their respective directories.
ifneq ($(wildcard build),)
	$(SHELL) -c "rm -r build"
endif
ifneq ($(wildcard dist),)
	$(SHELL) -c "rm -r dist"
endif
ifneq ($(wildcard python_http_parser.egg-info),)
	$(SHELL) -c "rm -r python_http_parser.egg-info"
endif

check-build:
	python -m twine check $(wildcard dist/*)

build:
	python -m build -o ./dist

upload:
	python -m twine upload -r pypi $(wildcard dist/*)

test:
	python -m pytest tests

bench:
	python -m pytest bench

lint:
	python -m pylint ./tests
	python -m pylint ./python_http_parser
	rstcheck $(wildcard ./*.rst)
	rstcheck $(wildcard ./docs/*.rst)

typecheck:
	python -m mypy .

.PHONY: check-build build upload test lint typecheck bench profile
