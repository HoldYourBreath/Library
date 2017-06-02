#!/usr/bin/env bash

# Fail on any error
set -e

python3 -m venv env

source env/bin/activate

pip3 install -r requirements.txt
