#!/bin/bash

#
# this script should be run from utils directory.
#
PROJECT_DIR='../'

# python code
echo "-------------------- PYTHON CODE --------------------"
find $PROJECT_DIR -iname '*py' | grep -vPe 'debug_toolbar|extension|svn|pyc|pep8' | grep -Pe '\.py$' | xargs wc -l | sort -n

# html code
echo "-------------------- HTML CODE --------------------"
find $PROJECT_DIR -iname '*html' | grep -vPe 'debug_toolbar|extension|svn|pyc|pep8' | grep -Pe '\.html$' | xargs wc -l | sort -n
