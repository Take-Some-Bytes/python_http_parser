# Shortcuts for running utility commands.

BENCH_MSG_ID?=0
BENCH_MODE?=both

clean-build:
	rm -rf build
	rm -rf dist
	rm -rf python_http_parser.egg-info

check-build:
	python -m twine check dist/*

build:
	python -m build -o ./dist

upload:
	python -m twine upload -r pypi dist/*

test:
	python -m pytest

lint:
	python -m pylint ./tests
	python -m pylint ./python_http_parser
	python -m rstcheck ./**.rst
	python -m rstcheck ./docs/**.rst

typecheck:
	python -m mypy .

bench:
	python ./bench/run.py -t bench -i $(BENCH_MSG_ID) -m $(BENCH_MODE)

profile:
	python ./bench/run.py -t profile -i $(BENCH_MSG_ID) -m $(BENCH_MODE)

.PHONY: check-build build upload test lint typecheck bench profile
