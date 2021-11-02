#!/bin/bash

python setup.py bdist_egg --exclude-source-files
wheel convert dist/*