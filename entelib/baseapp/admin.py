from django.contrib import admin
from entelib.baseapp.models import Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental

# register models in admin's site
for model in [Location, State, Publisher, Picture, Author, Book, BookCopy, Reservation, Rental]:
    admin.site.register(model)

