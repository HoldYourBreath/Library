#!/usr/bin/env bash

# Fail on any error
set -e

# Setup the environment
echo -n "Setup python virtual environment.."
source scripts/bootstrap.sh >/dev/null
echo "Done"

# Fix PEP8
echo -n "Fix PEP8.."
python3 -m autopep8 --in-place --aggressive --verbose -r library tests
echo "Done"

# Check PEP8
echo -n "Check PEP8 conformance.."
python3 -m pep8 --show-source --show-pep8 --count library tests
echo "Done"
