#-*- coding=utf-8 -*- 

from django.db import models
# from django.db.models import User
from django.contrib.auth.models import User


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30) #TODO maxlen
    remarks = models.CharField(max_length=50) #TODO potrzebne? jakie pole?

class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30) #TODO maxlen
    is_available = models.BooleanField()

class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50) #TODO maxlen
   
class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.ImageField(upload_to='book_pictures') #TODO: ograniczenia obrazka
    
class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50) #TODO maxlen

    def __unicode__(self):
        return self.name

class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    author = models.ManyToManyField(Author)
    
    def __unicode__(self):
        return self.title

class BookCopy(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book)
    location = models.ForeignKey(Location)
    state = models.ForeignKey(State)
    publisher = models.ForeignKey(Publisher)
    year = models.IntegerField()
    publication_nr = models.IntegerField()
    picture = models.ForeignKey(Picture) 
    description = models.TextField()

    class Admin: pass

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    book_copy = models.ForeignKey(BookCopy)
    for_whom = models.ForeignKey(User, related_name='user')
    start_date = models.DateField()
    end_date = models.DateField()
    who_reserved = models.ForeignKey(User, related_name='reserver')
    who_cancelled = models.ForeignKey(User, related_name='canceller')
    
    class Admin: pass

    def __unicode__(self):
        return u'id: ' + unicode(self.id) 
    

class Rental(models.Model):
    id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey(Reservation)
    start_date = models.DateTimeField() #(auto_now_add=True)
    end_date = models.DateTimeField()
    who_handed_out = models.ForeignKey(User, related_name='giver')
    who_received = models.ForeignKey(User, related_name='receiver')

    def __unicode__(self):
        return u'id: ' + unicode(self.id) 




# example of how we customize admin page (here Book's admin page)    
# # see: http://docs.djangoproject.com/en/1.1/ref/contrib/admin/
# from django.contrib import admin
# class BookAdmin(admin.ModelAdmin):
#     def upcased_title(obj):
#         return ("%s" % (obj.title.upper(),))
#     upcased_title.short_description = 'UPCASED TITLE'

#     search_fields = ['title', 'author']
#     list_display = [upcased_title, 'title', 'author','is_reserved', 'status', 'localization']
#     list_display_links = ['title', 'author']
#     list_filter = ['status', 'localization']
#     radio_fields = {'status': admin.HORIZONTAL}
#     save_on_top = True   # display Save/... buttons also on top of the form
# #     list_per_page = 3  # pagination

#     fieldsets = (
#         ('Basic informations', {
#                 'description': '<span style="color:red; font: 14pt bold;">hello world</span>',
#                 'classes': ['wide','extrapretty'],
#                 'fields': ['title', 'author']
#         }),
#         ('Additional options', {
#                 'fields' : ['localization', 'status'],
#                 'classes': ['wide']
#         #     'classes': ('collapse',),
#         #     'fields': ('enable_comments', 'registration_required', 'template_name')
#         }),
#     )
