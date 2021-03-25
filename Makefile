ifeq (, $(shell which python))
	ifeq (, $(shell which python3))
		$(error "Python executable not found.")
	endif
endif

# Determine which python we need to use.
# This is much safer than just calling `python`, since not all computers
# have `python` as the name of the executable.
py_ver = $(shell python -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)")
py_ver_required = 3.0
py_ver_ok = $(shell python -c 'import sys;print(int(float("%d.%d"% sys.version_info[0:2]) >= $(py_ver_required)))' )
py = python

ifeq ($(py_ver_ok), 0)
  py = python3
endif

check:
	$(py) -m twine check dist/*
clean:
	$(py) -m pip uninstall docutils build pytest
clean-build:
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./python_http_parser.egg-info
init:
	$(py) -m pip install --upgrade pip
	$(py) -m pip install docutils build pytest
build:
	$(py) -m build
upload:
	$(py) -m twine upload -r pypi dist/*
upload-test:
	$(py) -m twine upload -r testpypi dist/*
test:
	$(py) -m pytest
lint:
	$(py) -m pylint ./tests
	$(py) -m pylint ./python_http_parser

.PHONY: clean init build upload upload-test test
