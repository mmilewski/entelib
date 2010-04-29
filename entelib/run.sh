#!/bin/bash

# runserver docs:
#  http://docs.djangoproject.com/en/dev/intro/tutorial01/#the-development-server
#  http://docs.djangoproject.com/en/dev/ref/django-admin/#djadmin-runserver

python dbcreator.py
python manage.py runserver 8484
