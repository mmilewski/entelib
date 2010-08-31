
#
# USAGE:
#  This script should not be run standalone (probably will crash because of lack of imports)
#  Run shell plus first (python manage.py shell_plus), then import this module and run main()
#

class PermissionFixer():
    def __init__(self, quiet):
        self.quiet = quiet
        self.trace_prefix = 'PermissionFixer: '

    def trace(self, msg):
        if not self.quiet:
            print self.trace_prefix + msg

    def refresh_perms_for_group(self, group_name):
        """
        Sets permission to group found by group_name.
        If group doesn't exist, DoesNotExist will be raised
        """
        from entelib.dbfiller_perms import perms_by_group
        from django.contrib.auth.models import Group
        self.trace('Refreshing permissions for group: %s' % group_name)
        perms = perms_by_group[group_name]
        try:
            g = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            self.trace('Group %s doesnt exist' % group_name)
            raise
        g.permissions = perms
        g.save()
    
    def fix_perms(self):
        from django.contrib.auth.models import Permission, Group, User
        from entelib.dbfiller_perms import groups
        a_group = groups['admins']
        l_group = groups['librarians']
        r_group = groups['readers']
    
        self.refresh_perms_for_group(a_group)
        self.refresh_perms_for_group(l_group)
        self.refresh_perms_for_group(r_group)

def main(quiet=True):
    """
    Args:
        quiet -- if False then nothing will be printed out, else it may be.
                 Though it doesn't mean exceptions will not be raised.
    """
    pf = PermissionFixer(quiet=quiet)
    pf.fix_perms()
