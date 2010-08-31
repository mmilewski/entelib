#!/bin/bash

manage_file=manage.py
groups_fixture=baseapp/fixtures/small_db-groups.json

if [ -f $manage_file ]
then
    if [ -f $groups_fixture ]; then
        true
    else
        echo -e "File $groups_fixture doesn't exist. This may be a bug."
        sleep 3
    fi
        
    echo -e "Group.objects.all().delete() \nPermission.objects.all().delete()" | python $manage_file shell_plus
    python $manage_file syncdb 
    echo -e "from dbfiller import populate_groups as pg \npg()" | python $manage_file shell_plus
    python $manage_file dumpdata --indent 4 auth.Group > $groups_fixture
else
    echo -e 'You are doing it wrong. Run this script from app dir (where manage.py is), like:\n\tsh utils/fix_perms.sh'
fi
