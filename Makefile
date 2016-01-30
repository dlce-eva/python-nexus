
build:
	python setup.py sdist bdist_wheel

release:
	python setup.py sdist bdist_wheel upload

test:
	py.test --cov
