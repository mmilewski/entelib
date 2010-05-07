from django.contrib import admin
from entelib.baseapp.models import CustomUser, Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental, Phone, PhoneType, CostCenter

# register models in admin's site
for model in [CustomUser, Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental, Phone, PhoneType, CostCenter]:
    admin.site.register(model)

