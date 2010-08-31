# -*- coding: utf-8 -*-

from baseapp.utils import pprint
from django.db import models
from django.contrib.auth.models import User, Group  #, UserManager, Permission
import models_config as CFG
from django.db.models import signals
from django.core.exceptions import ValidationError
import datetime

#import settings

APPLICATION_NAME = 'baseapp'     # should be read from somewhere, I think

class Feedback(models.Model):
    when = models.DateTimeField(auto_now_add=True)
    who = models.CharField(max_length=100)
    msg = models.TextField()
    agent = models.TextField()

class EmailLog(models.Model):
    """
    Contains information about sent emails.
    """
    sender = models.CharField(max_length=CFG.emaillog_sender_len)
    receiver = models.CharField(max_length=CFG.emaillog_receiver_len)
    sent_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    subject = models.CharField(max_length=CFG.emaillog_subject_len)
    body = models.CharField(max_length=CFG.emaillog_body_len)

    def __unicode__(self):
        sent_date = self.sent_date.strftime('%d.%m.%Y %H:%M')
        return u"[%s] FROM: %s TO: %s BODY: %s" % (sent_date, self.sender, self.receiver, self.body)

    class Meta:
        permissions = (
            ('list_emaillog', 'Can list email logs'),
            )


class ConfigurationValueType(models.Model):
    """
    Type of value for key in Configuration.
    """
    name = models.CharField(max_length=CFG.configurationVT_name_len, primary_key=True)

    def __unicode__(self):
        return '%s' % (self.name,)

    class Meta:
        unique_together = (('name',),)


class Configuration(models.Model):
    """
    Here all config options are stored as (key, value) pairs.
    Any option can be customized by user in UserConfiguration model, 
    but only if can_override is True.
    If user will customize option that has can_override=False, it will has no effect.
    """
    key = models.CharField(max_length=CFG.configuration_key_len, primary_key=True)
    value = models.CharField(max_length=CFG.configuration_value_len)
    description = models.CharField(max_length=CFG.configuration_descirption_len)
    can_override = models.BooleanField(default=True)
    type = models.ForeignKey(ConfigurationValueType)

    class Meta:
        permissions = (
            ('list_config_options', "Can list configuration's options"),
            ('load_default_config', "Can load default values of configuration"),
            ('edit_option', "Can edit config option"),
            )

    def __unicode__(self):
        can_override_str = '+' if self.can_override else '-'
        return u'[%s] %s => %s' % (can_override_str, self.key, self.value)

    def __eq__(self, other):
        return \
            isinstance(other, Configuration) and \
            self.key          == other.key          and \
            self.value        == other.value        and \
            self.description  == other.description  and \
            self.can_override == other.can_override


class UserConfiguration(models.Model):
    """
    Set of options overrided by user. Option is overrided only if can_override is True in Configuration model.
    This model contains only overrided values, NOT all - so it is a subset 
    of Configuration if only keys are considered.
    If user will customize option that has can_override=False, it will has no effect.
    """
    option = models.ForeignKey(Configuration)
    user = models.ForeignKey(User)
    value = models.CharField(max_length=CFG.configuration_value_len)

    class Meta:
        verbose_name = 'Configuration per user'
        verbose_name_plural = 'Configurations per user'
        unique_together = (('option', 'user'),)
    
    def __unicode__(self):
        can_override_str = '+' if self.option.can_override else '-'
        return u"[%s] %s => %s" % (can_override_str, self.option.key, self.value)


class PhoneType(models.Model):
    """
    Phone type description.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.phonetype_name_len, unique=True)
    verify_re = models.CharField(max_length=CFG.phonetype_verify_re_len, blank=True)
    description = models.CharField(max_length=CFG.phonetype_description_len, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        unique_together = (('name',),)


class Phone(models.Model):
    """
    A broadly defined telephone: VoIP, mobile, fax, ...
    """
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(PhoneType)
    value = models.CharField(max_length=CFG.phone_value_len)

    def __unicode__(self):
        return u"%s: %s" % (unicode(self.type), unicode(self.value))

    def __eq__(self, other):
        return isinstance(other,Phone) and \
               self.id == other.id and \
               self.type == other.type and \
               self.value == other.value


# class PermisionNotDefined(Exception):
#     pass


class UserProfile(models.Model):
    """
    User with some extra fields like phone numbers.
    """

    user = models.OneToOneField(User, unique=True)
    shoe_size = models.PositiveIntegerField(null=True, blank=True)  # :)
    phone = models.ManyToManyField(Phone, null=True, blank=True)
    building = models.ForeignKey('Building', null=True, blank=True)
    awaits_activation = models.BooleanField()

    class Meta:
        permissions = (
            ("list_users", "Can list users"),
            ('view_own_profile', 'Can view his own profile'),
            ('view_others_profile', "Can view other people' profile"),
            ('edit_xname', "Can edit username, first name and last name"),
            ('list_reports', 'Can list reports'),     # FIXME: this shouldn't be here, but I don't know where is the right place for that, since no Report model is defined
            ('assign_user_to_groups', 'Can assign user to groups'), 
        )
        unique_together = (('user',),)

    def __init__(self, *args, **kwargs):
        """
        When new user is created we want him to not to be able to login yet. This is achieved by setting User.is_active to False.
        But sometimes we deactivate user and set his User.is_active to False as well. So, to avoid confusion, new users' field 
        awaits_activation is set to True. Later on, when he gets activated, the field will be set to False, so when he gets deactivated
        he is not regarded the same way as new users - admin won't see him when listing users to activate. This will work best with
        database trigger setting awaits_activation to False when is_active is set to True.
        """
        models.Model.__init__(self, *args, **kwargs)
        self.awaits_activation = True

    def __unicode__(self):
        return u"%s's profile" % self.user.username

    def __eq__(self, other):
        return \
            isinstance(other,UserProfile) and \
            self.user == other.user and \
            list(self.phone.all()) == list(other.phone.all()) and \
            self.building == self.building

    def is_librarian(self):
        lib_group = Group.objects.get(name='Librarians')
        return lib_group in self.user.groups.all()

    def is_admin(self):
        admin_group = Group.objects.get(name='Admins')
        return admin_group in self.user.groups.all()

    # def perm_exists(self, perm):
    #     """
    #     Chcecks whether given permission exists. Returns True or False respectively.
    #     """
    #     # query database (Permission table)
    #     prefixes = [APPLICATION_NAME + '.', 'sites.', 'auth.']
    #     for prefix in prefixes:
    #         if perm.startswith(prefix):
    #             perm = perm[len(prefix):]
    #             break
    #     perm_codename = perm
    #     try:
    #         Permission.objects.get(codename=perm_codename)
    #         return True             # no exception means we found it!
    #     except:
    #         pass

    #     # seek in models
    #     for klass in _defined_models:
    #         for perm_name, desc in klass._meta.permissions:
    #             if perm == ('%s.%s' % (APPLICATION_NAME, perm_name)):
    #                 if settings.DEBUG:
    #                     print 'Permission %s found in %s class' % (perm, str(klass._meta))
    #                 return True

    #     return False


    # def has_perm(self, perm):
    #     """
    #     Checks whether user not only has perminssion 'perm', but also whether such permission exists in project.
    #     Permissions defined in APP_NAME's models are checked like has_perm('baseapp.mypermission'),
    #     and has_perm('mypermission') is INCORRECT.
    #     """
    #     if not self.perm_exists(perm):
    #         raise PermisionNotDefined(perm)
    #     return User.has_perm(self, perm)


def create_profile_for_user(sender, instance, **kwargs):
    """ instance is an instance of User class. """
    try:
        UserProfile.objects.get(user__id=instance.id)
    except UserProfile.DoesNotExist:
        UserProfile(user=instance).save()

signals.post_save.connect(create_profile_for_user, sender=User, weak=False)


class Building(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.building_name_len)
    remarks = models.CharField(max_length=CFG.building_remarks_len, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        permissions = (
            ("list_buildings", "Can list buildings"),
            ("view_building", "Can see building's details"),
            )


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    building = models.ForeignKey(Building, blank=False, null=False)
    details = models.CharField(max_length=CFG.location_name_len)
    remarks = models.CharField(max_length=CFG.location_remarks_len, blank=True)
    maintainer = models.ManyToManyField(User, blank=True, null=True, verbose_name='Maintainers')

    def __unicode__(self):
        return u'%s: %s' % (self.building.name, self.details)

    class Meta:
        ordering = ['building__name', 'details']
        permissions = (
            ("list_locations", "Can list locations"),
            ("view_location", "Can see location's details"),
            )
        unique_together = (('building', 'details'),)



class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.state_name_len)
    is_available = models.BooleanField()
    is_visible = models.BooleanField()
    description = models.CharField(blank=True, null=True, max_length=CFG.state_description_len)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        permissions = (
            ("list_states", "Can list states"),
            ("view_state", "Can see state's details"),
            )


class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.publisher_name_len)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        permissions = (
            ("list_publishers", "Can list publishers"),
            ("view_publisher", "Can see publisher's details"),
            )


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.author_name_len)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        permissions = (
            ("list_authors", "Can list authors"),
            ("view_author", "Can see author's details"),
            )


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.category_name_len)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = (('name',),)
        permissions = (
            ("list_categories", "Can list categories"),
            ("view_category", "Can see category's details"),
            )


class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=CFG.book_title_len)
    author = models.ManyToManyField(Author)
    category = models.ManyToManyField(Category, blank=True, null=True)

    def __unicode__(self):
        # return u'%s %s' % (self.title, unicode(self.author.all()))
        return u'%s' % (self.title, )

    class Meta:
        permissions = (
            ("list_books", "Can list books"),
            )
        unique_together = (('title',),)


class BookRequest(models.Model):
    id = models.AutoField(primary_key=True)
    who = models.ForeignKey(User, blank=False, null=False)
    when = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    book = models.ForeignKey(Book, blank=True, null=True)
    info = models.TextField()

    class Meta:
        permissions = (
            ("list_bookrequests", "Can list book requests"),
            )

    def __unicode__(self):
        title = self.book.title if self.book else 'n/a'
        return u'Request for: (%s) %s' % (title, self.info[:30], )

    def __eq__(self, other):
        return \
            isinstance(other,BookRequest) and \
            self.id   == other.id   and \
            self.who  == other.who  and \
            self.when == other.when and \
            self.book == other.book and \
            self.info == other.info


class CostCenter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFG.costcenter_name_len)

    def __unicode__(self):
        return u'CC %s' % (self.name, )

    class Meta:
        permissions = (
            ("list_costcenters", "Can list cost centers"),
            ("view_costcenter", "Can see cost center's details"),
            )
        unique_together = (('name',),)


def sane_year(year):
    if not year: return
    if year > datetime.date.today().year:
        raise ValidationError(u"C'mon, it couldn't be published in the FUTURE")
    if year < 1900:
        raise ValidationError(u"C'mon, it can't be THAT old")
            

class BookCopy(models.Model):
    id = models.AutoField(primary_key=True)
    # shelf_mark = models.PositiveIntegerField()                                # big number for client's internal use
    shelf_mark = models.CharField(max_length=CFG.shelf_mark_len, unique=True)
    book = models.ForeignKey(Book)
    cost_center = models.ForeignKey(CostCenter)
    location = models.ForeignKey(Location)
    state = models.ForeignKey(State)
    publisher = models.ForeignKey(Publisher, null=True)
    year = models.IntegerField(blank=True, null=True, validators=[sane_year])
    publication_nr = models.IntegerField(null=True, blank=True)
    toc = models.TextField(blank=True, verbose_name="Table of contents")                   # table of contents
    toc_url = models.CharField(blank=True, max_length=CFG.copy_toc_url_len, verbose_name="Link to table of contents")    # external link to TOC
    description = models.TextField(blank=True)                                             # description
    description_url = models.CharField(blank=True, max_length=CFG.copy_desc_url_len)       # and/or a link to description

    def __unicode__(self):
        return u'%s [%d, copy]' % (self.book.title, self.id, )

    class Meta:
        verbose_name_plural = 'Book copies'
        unique_together = (('shelf_mark',),)

    class Admin:
        pass


class Reservation(models.Model):
    """
    Class for book reservations.

    who_cancelled and when_cancelled fields should be normally NULL.
    If who_cancelled is NULL and when_cancelled is not, it means reservation expired.

    end_date is set when performing rental. It can be max of #TODO field in configuration table.
    """
    id = models.AutoField(primary_key=True)
    book_copy = models.ForeignKey(BookCopy)
    for_whom = models.ForeignKey(User, related_name='reader')
    start_date = models.DateField()
    end_date = models.DateField()
    who_reserved = models.ForeignKey(User, related_name='reserver')
    when_reserved = models.DateTimeField(auto_now_add=True)
    who_cancelled = models.ForeignKey(User, related_name='canceller', null=True, blank=True)
    when_cancelled = models.DateTimeField(null=True, blank=True)
    active_since = models.DateField(null=True, blank=True)
    shipment_requested = models.BooleanField()

    class Admin:
        pass

    class Meta:
        permissions = (
            ("change_own_reservation", "Can change owned reservations"),
            )

    def __unicode__(self):
        return unicode(self.id) + ', ' + u'For Mr/Ms ' + self.for_whom.first_name + u' ' + self.for_whom.last_name + '. ' + unicode(self.book_copy)

    def __eq__(self, other):
        return \
          isinstance(other,Reservation) and \
          self.id == other.id and \
          self.book_copy          == other.book_copy and \
          self.for_whom           == other.for_whom and \
          self.start_date         == other.start_date and \
          self.end_date           == other.end_date and \
          self.who_reserved       == other.who_reserved and \
          self.when_reserved      == other.when_reserved and \
          self.who_cancelled      == other.who_cancelled and \
          self.when_cancelled     == other.when_cancelled and \
          self.active_since       == other.active_since and \
          self.shipment_requested == other.shipment_requested


class Rental(models.Model):
    """
    Stores rental information.

    Every rental must be connected with some reservation. Reservation holds informations on who
    rented (reservation.for_whom), which book (reservation.book_copy) and when he is obligated
    to return it (reservation.end_date).

    start_date is when book was rented

    end_date is when book was returned (may be NULL if book is still rented)

    who_handed_out is librarian who gave away book

    who_received is librarian who received book
    """
    id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey(Reservation)
    start_date = models.DateTimeField()   # (auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    who_handed_out = models.ForeignKey(User, related_name='giver')
    who_received = models.ForeignKey(User, related_name='receiver', null=True, blank=True)

    def __unicode__(self):
        return u'id: ' + unicode(self.id)

    def __eq__(self, other):
        return \
          isinstance(other,Rental) and \
          self.id             == other.id and \
          self.reservation    == other.reservation and \
          self.start_date     == other.start_date and \
          self.end_date       == other.end_date and \
          self.who_handed_out == other.who_handed_out and \
          self.who_received   == other.who_received




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


## Defined model list contains all classes where has_perm will look for permissions.
## If you know how to do this automaticaly, feel free to update :) I think it's possible. It's enough to walk through all classes and check for Meta inner class existance
#_defined_models = [Configuration, PhoneType, Phone, User, UserProfile, Location, State, Publisher, Author, Book, CostCenter, BookCopy, Reservation, Rental]
