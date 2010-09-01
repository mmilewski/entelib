from pprint import pprint
from os.path import abspath, dirname, join, exists
import sys
libs_path = join(dirname(abspath(__file__)),'../..','libs')
django_path = join(libs_path,'Django-1.2.1')
imaging_path = join(libs_path,'Imaging-1.1.7')
sys.path.insert(0, imaging_path)
sys.path.insert(0, django_path)
from django.contrib.auth.models import User

import pickle
filename = raw_input(['From what file recover passwords? [Enter] for "passwords.back"'])
if not filename:
    filename = 'passwords'
filename = 'migration/' + filename

file = open(filename, 'r')
email_hash_list = pickle.load(file)
for email, password in email_hash_list:
    try:
        u = User.objects.get(email=email)
    except:
        pprint(email+' nie istnieje')
    u.password=password
    u.save()
file.close()
