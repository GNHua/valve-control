#!/bin/sh

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. && pwd )"
date >> $PROJECT_ROOT/log.txt 
python $PROJECT_ROOT/run.py >> $PROJECT_ROOT/log.txt &

