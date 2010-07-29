#!/bin/bash

# runserver docs:
#  http://docs.djangoproject.com/en/dev/intro/tutorial01/#the-development-server
#  http://docs.djangoproject.com/en/dev/ref/django-admin/#djadmin-runserver

# Running ./run.sh new  will recreate db.

RUN_VALIDATION='python manage.py validate'
RUN_TESTS='python manage.py test baseapp'
RUN_SERVER='python manage.py runserver_plus'

if [ $# -gt 0 ]; then
    if [[ (($1 = "new" || $2 = "new")) ]]; then
        python dbcreator.py new
    elif [[ (($1 = "notest" || $2 = "notest")) ]]; then
        RUN_TESTS=''
    else
        echo -e "Given ARGUMENT is INCORRECT. Possible commands:"
        echo -e "\tnew - recreate database"
        echo -e "\tnotest - run without running tests"
        echo
        exit 1
    fi
else
    python dbcreator.py
fi

$RUN_VALIDATION
$RUN_TESTS
$RUN_SERVER 10.154.4.75:8484 || $RUN_SERVER 10.154.7.179:8484 || $RUN_SERVER 8484
