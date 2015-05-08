#!/bin/sh

./temp/venv/bin/nosetests --exe -w ./main/ --with-gae -v -s tests
