from django.contrib import admin
from entelib.baseapp.models import Person, Book, Rental, Reservation


for c in [Person, Book, Rental, Reservation]:
    admin.site.register(c)

