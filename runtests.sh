#!/bin/sh

./temp/venv/bin/nosetests --exe -w ./main/ --with-gae $2 $3 tests/$1 
