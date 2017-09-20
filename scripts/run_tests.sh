#!/usr/bin/env bash

# Fail on any error
set -e

# Setup the environment
echo -n "Setup python virtual environment.."
source scripts/bootstrap.sh >/dev/null
echo "Done"

# Run tests
echo -n "Run tests"
python3 -m coverage run --rcfile=scripts/.coveragerc -m unittest discover
echo "Generate coverage report"
python3 -m coverage html
python3 -m coverage report -m
echo "Tests done.. Open htmlcov/index.html for more statistics"

# Run PEP8 conformance
echo -n "Check PEP8 conformance.."
python3 -m pep8 --show-source --show-pep8 --count library tests
echo "Done"

# Don't fail on errors
set +e

echo -n "Search for uncommited changes in the index.."
git diff-index --quiet HEAD --
if [ $? != 0 ]; then
    echo "Warning!"
    echo "!!!!!!!!!! You have uncommited changes in the index !!!!!!!!!!"
    exit 1
fi

echo "Done"

echo "All OK"
