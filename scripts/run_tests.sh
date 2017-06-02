#!/usr/bin/env bash

# Fail on any error
set -e

# Setup the environment
echo -n "Setup python virtual environment.."
source scripts/bootstrap.sh >/dev/null
echo "Done"

# Run tests
echo -n "Run tests"
python3 -m unittest discover

# Run PEP8 conformance
echo -n "Check PEP8 conformance.."
python3 -m pep8 --show-source --show-pep8 --count --exclude "library/library.py" library tests
echo "Done"

echo -n "Run coverage"
# Get coverage
python3 -m coverage run -m unittest discover
echo "Generate coverage report"
python3 -m coverage html
python3 -m coverage report -m

echo "All done.. Open htmlcov/index.html for more statistics"

