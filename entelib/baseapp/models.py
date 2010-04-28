#-*- coding=utf-8 -*- 

from django.db import models
# from django.db.models import User
from django.contrib.auth.models import User
import models_config as CFG

# TODO:
#   - telephone as a separate table: voip, mobile, phone
#   - fields in location are probably: building, floor, room, name, telephone* (zero or more). Name is like 'Tweety' or 'Scooby'

class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.location_name_len)
    remarks = models.CharField(max_length=CFG.location_remarks_len, blank=True)

    def __unicode__(self):
        return self.name

class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.state_name_len)
    is_available = models.BooleanField()

    def __unicode__(self):
        return self.name

class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.publisher_name_len)

    def __unicode__(self):
        return self.name
   
class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=CFG.picture_description_len)
    file = models.ImageField(upload_to=CFG.picture_upload_to) #TODO: ograniczenia obrazka

    def __unicode__(self):
        return self.description

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.author_name_len)

    def __unicode__(self):
        return self.name

class Book(models.Model):
    class Meta:
        permissions = (
            ("can_view", "Can view things"),
            )
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=CFG.book_title_len)
    author = models.ManyToManyField(Author)  # authors?
    
    def __unicode__(self):
        # return u'%s %s' % (self.title, unicode(self.author.all()))
        return u'%s' % (self.title, )

class BookCopy(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book)
    location = models.ForeignKey(Location)
    state = models.ForeignKey(State)
    publisher = models.ForeignKey(Publisher)
    year = models.IntegerField()
    publication_nr = models.IntegerField()
    picture = models.ForeignKey(Picture, null=True, blank=True) 
    description = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s [copy]' % (self.book.title,)

    class Meta:
        verbose_name_plural = 'Book copies'

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
