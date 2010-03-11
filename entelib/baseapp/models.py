#-*- coding=utf-8 -*- 

from django.db import models


class Book(models.Model):
    STATUS_CHOICES = (
            ('a', 'available'),
            ('d',  'disabled'),
        )
    #TODO: jakie rzeczywiście chcemy stany?
    # temporarily unavailable?
        

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    #TODO: jak długi tytuł/autor?
    author = models.CharField(max_length=50)
    localization = models.CharField(max_length=50, blank=True)
    #TODO: o co chodzi z localization?
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)

    def is_reserved(self):
        ''' Returns boolean information (True/False) whether the book is reserved.'''
        import random
        # FIXME. quick hack. information from Reservation should be pulled
        return random.choice([True, False])
    is_reserved.short_description = 'is reserved'

    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + unicode(self.author) + u': ' + unicode(self.title)

# see: http://docs.djangoproject.com/en/1.1/ref/contrib/admin/
from django.contrib import admin
class BookAdmin(admin.ModelAdmin):
    def upcased_title(obj):
        return ("%s" % (obj.title.upper(),))
    upcased_title.short_description = 'UPCASED TITLE'

    search_fields = ['title', 'author']
    list_display = [upcased_title, 'title', 'author','is_reserved', 'status', 'localization']
    list_display_links = ['title', 'author']
    list_filter = ['status', 'localization']
    radio_fields = {'status': admin.HORIZONTAL}
    save_on_top = True   # display Save/... buttons also on top of the form
#     list_per_page = 3  # pagination

    fieldsets = (
        ('Basic informations', {
                'description': '<span style="color:red; font: 14pt bold;">hello world</span>',
                'classes': ['wide','extrapretty'],
                'fields': ['title', 'author']
        }),
        ('Additional options', {
                'fields' : ['localization', 'status'],
                'classes': ['wide']
        #     'classes': ('collapse',),
        #     'fields': ('enable_comments', 'registration_required', 'template_name')
        }),
    )

admin.site.register(Book, BookAdmin)

    

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    info = models.CharField(max_length=30)
    #TODO: jak rzeczywiście pracujemy z użytkownikiem

    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + 'info: ' + unicode(self.info)


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book)
    person = models.ForeignKey(Person)
    starts = models.DateField()
    expires = models.DateField()
    class Admin: pass

    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + unicode(self.book) + u': reserved from ' + unicode(self.starts) + u' until ' + unicode(self.expires)
    

class Rental(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book)
    person = models.ForeignKey(Person)
    started = models.DateTimeField() #(auto_now_add=True)
    #who_handed_out = models.ForeignKey(Person)
    #TODO: czy chcemy automatyczne dodawanie bieżącej daty?
    ended = models.DateTimeField(blank=True, null=True)
    #TODO: id bibliotekarza?
    #who_received = models.ForeignKey(Person)

    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + unicode(self.book) + u' rented ' + unicode(self.started) + u' to ' + unicode(self.person)




    
    

