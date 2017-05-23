#!/bin/bash

# Fail on any error
set -e

# Run tests
echo "!!! First run tests !!!"
python -m unittest discover

echo "!!! Run tests again but this time with coverage" !!!
# Get coverage
coverage run -m unittest discover
coverage html
coverage report -m

echo "All done.. Open htmlcov/index.html for more statistics"
