#!/bin/bash

# runserver docs:
#  http://docs.djangoproject.com/en/dev/intro/tutorial01/#the-development-server
#  http://docs.djangoproject.com/en/dev/ref/django-admin/#djadmin-runserver

# Running ./run.sh new  will recreate db.

if [ $# -gt 0 ]; then
    if [ $1 = "new" ]; then
        python dbcreator.py new
    else
        echo -e "Given ARGUMENT is INCORRECT. Possible commands:"
        echo -e "\tnew - recreate database"
        echo
        exit 1
    fi
else
    python dbcreator.py
fi

python manage.py validate
python manage.py test baseapp
python manage.py runserver_plus 10.154.5.211:8484 || python manage.py runserver_plus 8484
