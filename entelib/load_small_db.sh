#!/bin/bash

echo "yes"|./manage.py reset_db
echo "no" | ./manage.py syncdb
./manage.py loaddata small_db
