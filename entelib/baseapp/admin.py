from django.contrib import admin
from entelib.baseapp.models import CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from entelib.baseapp.models import Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental, Phone, PhoneType, CostCenter

admin.site.unregister(User)
admin.site.register(CustomUser, UserAdmin)


# register models in admin's site
for model in [Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental, Phone, PhoneType, CostCenter]:
    admin.site.register(model)
