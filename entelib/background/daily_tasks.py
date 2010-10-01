import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from os.path import abspath, dirname, join, exists
project_path = join(dirname(abspath(__file__)), '..')
app_path = join(project_path, '..', 'baseapp')
libs_path = join(dirname(abspath(__file__)),'../..','libs')
django_path = join(libs_path,'Django-1.2.1')
imaging_path = join(libs_path,'Imaging-1.1.7')
sys.path.insert(0, imaging_path)
sys.path.insert(0, django_path)
sys.path.insert(0, project_path)
sys.path.insert(0, app_path)


from baseapp.models import *
from django.contrib.auth.models import User
from baseapp.utils import today, after_days
from baseapp.config import Config
from datetime import datetime
import baseapp.views_aux as aux
import baseapp.emails as mail


for r in Rental.objects.all():
    if not r.end_date :
        if r.reservation.end_date < today():  # reservation expired: notify reader every day
            mail.overdued(r)
        if r.reservation.end_date == after_days(Config().get_int('due_remind_time')):
            mail.returnal_date_coming(r)      # reservation will expire soon: notify reader

for r in Reservation.objects.filter(aux.Q_reservation_active):
    if not r.active_since and aux.is_reservation_rentable(r):
        # reservation has just become active - notify user
        r.active_since = today()
        r.save()
        mail.reservation_active(r)
    
    if r.active_since and r.active_since <= after_days(-1*Config().get_int('reservation_rush')):
        r.when_cancelled = datetime.now()
        r.save()
        mail.reservation_expired(r)
        
backup_name = "backup_{0}".format(today().isoformat())
backup_dir = "../backup/" # this needs to have slash at the end
os.system("pg_dump --format=p | gzip > {0}{1}.gz".format(backup_dir, backup_name))


# to restore db: first totally clean db, uncompress file:
# gunzip backup_2010-10-01.gz
# then, from bash restore database
# psql -f backup_2010-10-01
