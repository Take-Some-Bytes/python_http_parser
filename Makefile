# Shortcuts for running utility commands.

ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname)  # same as "uname -s"
endif

ifeq ($(DETECTED_OS),Windows)
    SHELL := powershell.exe
endif

PROFILE_ITERS ?= 100000
PROFILE_API ?= stream_parser_req

# Put this first for obvious reasons
help:
	@echo "Nothing specified, nothing done"
	@echo "Available commands:"
	@echo "  - clean-build: cleans build directories"
	@echo "  - check-build: ensures built files are valid"
	@echo "  - build: build python wheels and source dists"
	@echo "  - upload: upload build to PyPI"
	@echo "  - test: run PyTest unit tests"
	@echo "  - bench: run benchmarks, powered by pytest-benchmark"
	@echo "  - profile: profile certain APIs"
	@echo "  - lint: lint Python and ReStructureText files"
	@echo "  - typecheck: perform typechecking using mypy"

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

profile:
	python -m bench -a $(PROFILE_API) -i $(PROFILE_ITERS)

lint:
	python -m pylint ./tests
	python -m pylint ./python_http_parser
	rstcheck $(wildcard ./*.rst)

typecheck:
	python -m mypy .

.PHONY: check-build build upload test lint typecheck bench profile help
