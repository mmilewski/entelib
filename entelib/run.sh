#!/bin/bash

# runserver docs:
# ----------
#  http://docs.djangoproject.com/en/dev/intro/tutorial01/#the-development-server
#  http://docs.djangoproject.com/en/dev/ref/django-admin/#djadmin-runserver

# USAGE:
# ----------
# ./run.sh new              will create fresh new db and fill it with random data -- see dbfiller.py
# ./run.sh notest           will run server omitting testing phase
# ./run.sh smalldb          will load database from smalldb.json fixture. It permanently overrides current db.
#
# Combinations of above commands are allowed, but there is no protection against i.e. calling './run.sh smalldb new'
#

RUN_VALIDATION='python manage.py validate'
RUN_TESTS='python manage.py test baseapp'
RUN_SERVER='python manage.py runserver_plus'

if [ $# -gt 0 ]; then
    if [[ $1 = "smalldb" ]]; then 
        rm database/database.db
        echo "no" | python manage.py syncdb
        python manage.py loaddata small_db.json small_db-configuration.json small_db-groups.json
    fi
    if [[ (($1 = "new" || $2 = "new")) ]]; then
        python dbcreator.py new
    fi
    if [[ (($1 = "notest" || $2 = "notest")) ]]; then
        RUN_TESTS=''
    fi
else
    python dbcreator.py
fi

$RUN_VALIDATION
$RUN_TESTS
$RUN_SERVER 8484 #if you want your development server to be visible from outside use $RUN_SERVER 1.1.1.1 80  # substituting 1.1.1.1 with your computer ip and 80 with port of your choice
