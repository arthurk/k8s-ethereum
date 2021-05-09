#!/bin/bash

set -eu
cd $(dirname $0)

pipenv run python ./create_site.py
