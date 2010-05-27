from django.contrib import admin
from entelib.baseapp.models import CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from entelib.baseapp.models import Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental, Phone, PhoneType, CostCenter, Category


class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    actions = ['activate_users', 'deactivate_users']

    # see /usr/lib/pymodules/python2.6/django/contrib/admin/actions.py
    # see http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/

    def activate_users(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        message_bit = "1 account was" if rows_updated == 1 else "%s accounts were" % rows_updated
        self.message_user(request, "%s successfully activated." % message_bit)
    activate_users.short_description = "Activate selected accounts"

    def deactivate_users(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        message_bit = "1 account was" if rows_updated == 1 else "%s accounts were" % rows_updated
        self.message_user(request, "%s successfully deactivated." % message_bit)
    deactivate_users.short_description = "Deactivate selected accounts"


admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)


# register models in admin's site
for model in [Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental, Phone, PhoneType, CostCenter, Category]:
    admin.site.register(model)
