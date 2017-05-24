#!/bin/bash

# Fail on any error
set -e

# Run tests
echo "!!! First run tests !!!"
python3 -m unittest discover

echo "!!! Run tests again but this time with coverage" !!!
# Get coverage
coverage3 run -m unittest discover
coverage3 html
coverage3 report -m

echo "All done.. Open htmlcov/index.html for more statistics"
