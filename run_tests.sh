#!/bin/bash

# Fail on any error
set -e

# Run tests
echo "!!! First run tests !!!"
python3 -m unittest discover

# Run PEP8 conformance
echo "!!! Check PEP8 conformance !!!"
python3 -m pep8 --show-source --show-pep8 --count --exclude "library/library.py" library tests
echo "PEP8 OK..."

echo "!!! Run tests again but this time with coverage" !!!
# Get coverage
python3 -m coverage run -m unittest discover
python3 -m coverage html
python3 -m coverage report -m

echo "All done.. Open htmlcov/index.html for more statistics"

