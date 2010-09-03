#!/bin/bash
# restore permissions after update/add/remove of permissions/models to default
echo "from utils.fix_perms import main; main(quiet=False)" | python manage.py shell_plus
