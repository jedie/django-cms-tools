BROWSER ?= xdg-open
PYTHON_PACKAGE = django_cms_tools
TESTS_PACKAGE = tests

.PHONY: clean clean-test clean-pyc clean-build docs help requirements
.DEFAULT_GOAL := help

help:
	@echo "Available Makefile targets:"
	@echo
	@echo "dist           builds source and wheel package"
	@echo "install        install the package to the active Python environment"
	@echo "requirements   pip-compile requirements file templates"
	@echo "docs           generate Sphinx HTML documentation, including API docs"
	@echo "py-test        run tests via py.test with the default Python version"
	@echo "tox            run tests on every Python version with tox"
	@echo "flake8         run style checks and static analysis with flake8"
	@echo "pylint         run style checks and static analysis with pylint"
	@echo "docstrings     check docstring presence and style conventions with pydocstyle"
	@echo "coverage       check code coverage with the default Python version"
	@echo "metrics        print code metrics with radon"
	@echo "clean          remove all build, test, coverage and Python artifacts"
	@echo "clean-build    remove Python file artifacts"
	@echo "clean-pyc      remove Python file artifacts"

## remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test

## remove build artifacts
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

## remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

## remove test and coverage artifacts
clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr reports/

## run tests quickly with the default Python
py-test:
	py.test -v django_cms_tools_tests/

## run tests on every Python version with tox
tox:
	tox

test-ci:
	python manage.py migrate
	tox

migrate:
	python manage.py migrate

runserver:
	python manage.py runserver

createsuperuser:
	python manage.py createsuperuser

## run style checks and static analysis with pylint
pylint:
	@-mkdir -p reports/
	@-pylint -f html $(PYTHON_PACKAGE) $(TESTS_PACKAGE) > reports/pylint.html
	@$(BROWSER) reports/pylint.html
	pylint $(PYTHON_PACKAGE) $(TESTS_PACKAGE)

## run style checks and static analysis with flake8
flake8:
	flake8 $(PYTHON_PACKAGE) $(TESTS_PACKAGE)

## check docstring presence and style conventions with pydocstyle
docstrings:
	pydocstyle $(PYTHON_PACKAGE)

lint: flake8 docstrings pylint

## check code coverage quickly with the default Python
coverage:
	@-mkdir -p reports/htmlcov
	coverage run --source $(PYTHON_PACKAGE) `which py.test`
	coverage report -m
	@coverage html -d reports/htmlcov
	@$(BROWSER) reports/htmlcov/index.html

## print code metrics with radon
metrics:
	radon raw -s $(PYTHON_PACKAGE) $(TEST_PACKAGE)
	radon cc -s $(PYTHON_PACKAGE) $(TEST_PACKAGE)
	radon mi -s $(PYTHON_PACKAGE) $(TEST_PACKAGE)

## generate Sphinx HTML documentation, including API docs
docs:
	rm -f docs/$(PYTHON_PACKAGE).rst
	sphinx-apidoc --no-toc -o docs/ $(PYTHON_PACKAGE)
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

## pip-compile requirements templates
requirements:
	$(MAKE) -C requirements all

## package and upload a release
release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

## builds source and wheel package
dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

## install the package to the active Python's site-packages
install: clean
	python setup.py install

publish: clean requirements
	python setup.py publish
