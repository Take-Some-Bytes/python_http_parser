# Shortcuts for running utility commands.

clean-build:
	rm -rf build
	rm -rf dist
	rm -rf python_http_parser.egg-info

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
