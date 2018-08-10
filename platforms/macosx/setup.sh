#!/bin/sh

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. && pwd )"
pip install -r $PROJECT_ROOT/app/requirements.txt 