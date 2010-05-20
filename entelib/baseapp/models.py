#-*- coding=utf-8 -*-

from django.db import models
# from django.db.models import User
from django.contrib.auth.models import User, UserManager, Permission
import models_config as CFG

APPLICATION_NAME = 'baseapp'     # should be read from somewhere, I think


# TODO:
#   this comment seems outdated...
#   - fields in location are probably: building, floor, room, name, telephone* (zero or more). Name is like 'Tweety' or 'Scooby'

class Configuration(models.Model):
    '''
    Key,Value pairs.
    '''
    key = models.CharField(max_length=CFG.configuration_key_len, primary_key=True)
    value = models.CharField(max_length=CFG.configuration_value_len)


class PhoneType(models.Model):
    '''
    Phone type description.
    '''
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.phonetype_name_len)
    verify_re = models.CharField(max_length=CFG.phonetype_verify_re_len, blank=True)
    description = models.CharField(max_length=CFG.phonetype_description_len, blank=True)

    def __unicode__(self):
        return unicode(self.name)


class Phone(models.Model):
    '''
    A broadly defined telephone: VoIP, mobile, fax, ...
    '''
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(PhoneType)
    value = models.CharField(max_length=CFG.phone_value_len)

    def __unicode__(self):
        return u"%s: %s" % (unicode(self.type), unicode(self.value))


class PermisionNotDefined(Exception):
    pass


class CustomUser(User):
    '''
    User with some extra fields like phone numbers.
    '''

    objects = UserManager()
    shoe_size = models.PositiveIntegerField(null=True, blank=True)  # :)
    phone = models.ManyToManyField(Phone, null=True, blank=True)

    class Meta:
        permissions = (
            ("list_users", "Can list users"),
        )


    def perm_exists(self, perm):
        '''
        Chcecks whether given permission exists. Returns True or False respectively.
        '''
        # query database (Permission table)
        prefixes = [APPLICATION_NAME + '.', 'sites.', 'auth.']
        for prefix in prefixes:
            if perm.startswith(prefix):
                perm = perm[len(prefix):]
                break
        perm_codename = perm
        try:
            Permission.objects.get(codename=perm_codename)
            return True             # no exception means we found it!
        except:
            pass

        # seek in models
        for klass in _defined_models:
            for perm_name, desc in klass._meta.permissions:
                if perm == ('%s.%s' % (APPLICATION_NAME, perm_name)):
                    print 'Permission %s found in %s class' % (perm, str(klass._meta))
                    return True

        return False


    def has_perm(self, perm):
        '''
        Checks whether user not only has perminssion 'perm', but also whether such permission exists in project.
        Permissions defined in APP_NAME's models are checked like has_perm('baseapp.mypermission'),
        and has_perm('mypermission') is INCORRECT.
        '''
        if not self.perm_exists(perm):
            raise PermisionNotDefined(perm)
        return User.has_perm(self, perm)


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
    is_visible = models.BooleanField()

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
    file = models.ImageField(upload_to=CFG.picture_upload_to)  # TODO: ograniczenia obrazka

    def __unicode__(self):
        return self.description


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.author_name_len)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.category_name_len)


class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=CFG.book_title_len)
    author = models.ManyToManyField(Author)


    def __unicode__(self):
        # return u'%s %s' % (self.title, unicode(self.author.all()))
        return u'%s' % (self.title, )


class CostCenter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.costcenter_name_len)

    def __unicode__(self):
        return u'CC %s' % (self.name, )


class BookCopy(models.Model):
    id = models.AutoField(primary_key=True)
    shelf_mark = models.PositiveIntegerField()                                # big number for client's internal use
    book = models.ForeignKey(Book)
    cost_center = models.ForeignKey(CostCenter)
    location = models.ForeignKey(Location)
    state = models.ForeignKey(State)
    publisher = models.ForeignKey(Publisher)
    year = models.IntegerField()
    publication_nr = models.IntegerField(blank=True)
    picture = models.ForeignKey(Picture, null=True, blank=True)
    toc = models.TextField(blank=True)                                        # table of contents
    toc_url = models.URLField(blank=True, max_length=CFG.copy_toc_url_len)    # external link to TOC
    description = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s [copy]' % (self.book.title,)

    class Meta:
        verbose_name_plural = 'Book copies'

    class Admin:
        pass


class Reservation(models.Model):
    '''
    Class for book reservations.

    who_cancelled and when_cancelled fields should be normally NULL.
    If who_cancelled is NULL and when_cancelled is not, it means reservation expired.

    end_date is set when performing rental. It can be max of #TODO field in configuration table.
    '''
    id = models.AutoField(primary_key=True)
    book_copy = models.ForeignKey(BookCopy)
    for_whom = models.ForeignKey(CustomUser, related_name='user')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    who_reserved = models.ForeignKey(CustomUser, related_name='reserver')
    when_reserved = models.DateTimeField(auto_now_add=True)
    who_cancelled = models.ForeignKey(CustomUser, related_name='canceller', null=True, blank=True)
    when_cancelled = models.DateTimeField(null=True, blank=True)
    active_since = models.DateField(null=True, blank=True)

    class Admin:
        pass

    def __unicode__(self):
        return u'For Mr/Ms ' + self.for_whom.first_name + u' ' + self.for_whom.last_name


class Rental(models.Model):
    '''
    Stores rental information.

    Every rental must be connected with some reservation. Reservation holds informations on who
    rented (reservation.for_whom), which book (reservation.book_copy) and when he is obligated
    to return it (reservation.end_date).

    start_date is when book was rented

    end_date is when book was returned (may be NULL if book is still rented)

    who_handed_out is librarian who gave away book

    who_received is librarian who received book
    '''
    id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey(Reservation)
    start_date = models.DateTimeField()   # (auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    who_handed_out = models.ForeignKey(CustomUser, related_name='giver')
    who_received = models.ForeignKey(CustomUser, related_name='receiver', null=True, blank=True)

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


# Defined model list contains all classes where has_perm will look for permissions.
# If you know how to do this automaticaly, feel free to update :) I think it's possible. It's enough to walk through all classes and check for Meta inner class existance
_defined_models = [Configuration, PhoneType, Phone, CustomUser, Location, State, Publisher, Picture, Author, Book, CostCenter, BookCopy, Reservation, Rental]
