# Determine which python we need to use.
# This is much safer than just calling `python`, since not all computers
# have `python` as the name of the executable.
py_ver = $(shell python -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)")
py_ver_required = 3.0
py_ver_ok = $(shell python -c 'import sys;\
  print(int(float("%d.%d"% sys.version_info[0:2]) >= $(py_ver_required)))' )
py = python

ifeq ($(py_ver_ok), 0)
  py = python3
endif

init:
	$(py) -m pip install docutils pep517 pytest
build:
	$(py) -m pep517.build
test:
	$(py) -m pytest
