#!/usr/bin/env sh
rm -rf dist
python setup.py sdist
twine upload dist/*
