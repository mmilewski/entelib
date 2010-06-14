from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User         # for reregistering User with modified UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm     # for MyUserAdmin
from entelib.baseapp.models import EmailLog, Building, Location, Configuration, State, Publisher, Picture, Author, Book, BookCopy, BookRequest, Reservation, Rental, Phone, PhoneType, CostCenter, Category, UserProfile

admin.site.disable_action('delete_selected')


class MyUserAdmin(UserAdmin):
    '''
    Overrides appearance & behaviour of Users tab in admin panel.
    '''
    # see: /usr/lib/pymodules/python2.6/django/contrib/auth/admin.py

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    list_display = ('username', 'first_name', 'last_name', 'email', 'profile', 'is_active', 'is_superuser', 'is_staff',)
    list_filter = ('is_staff', 'is_superuser', 'is_active',)
    actions = ['activate_users', 'deactivate_users',]
    ordering = ('is_active', 'username',)

    def profile(self, s):
        profile_url = '/entelib/admin/baseapp/userprofile/%d/' % s.id
        return '<a href="%s">%s</a>' % (profile_url, 'View profile')
    profile.short_description = "User's profile"
    profile.allow_tags = True

    def activate_users(self, request, queryset):
        '''
        Activates users passed in queryset.
        see: /usr/lib/pymodules/python2.6/django/contrib/admin/actions.py
        see: http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/
        '''
        rows_updated = queryset.update(is_active=True)
        message_bit = "1 account was" if rows_updated == 1 else ("%s accounts were" % rows_updated)
        self.message_user(request, "%s successfully activated." % message_bit)
    activate_users.short_description = "Activate selected accounts"

    def deactivate_users(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        message_bit = "1 account was" if rows_updated == 1 else ("%s accounts were" % rows_updated)
        self.message_user(request, "%s successfully deactivated." % message_bit)
    deactivate_users.short_description = "Deactivate selected accounts"


# reregister User with new ModelAdmin
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


# register models in admin's site
for model in [EmailLog, Building, Location, Configuration, State, Publisher, Picture, Author, Book, BookCopy, BookRequest, Reservation, Rental, Phone, PhoneType, CostCenter, Category, UserProfile]:
    admin.site.register(model)
