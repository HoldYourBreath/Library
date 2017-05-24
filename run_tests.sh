#!/bin/bash

# Fail on any error
set -e

# Run tests
echo "!!! First run tests !!!"
python3 -m unittest discover

echo "!!! Run tests again but this time with coverage" !!!
# Get coverage
python3 -m coverage run -m unittest discover
python3 -m coverage html
python3 -m coverage report -m

echo "All done.. Open htmlcov/index.html for more statistics"
