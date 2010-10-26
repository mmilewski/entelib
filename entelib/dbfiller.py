# -*- coding: utf-8 -*-

#
# TODO:
#  - rentals generating
#  - reservations generating

from sys import exit
from random import randint, choice, shuffle
from datetime import datetime, timedelta
from baseapp.models import *
from django.contrib.auth.models import Group

# define number of records to create
locations_count = 1
buildings_count = 1
authors_count = 1
publishers_count = 1
books_count = 0
states_count = 1
copies_count = 0
cost_centers_count = 1
rentals_count = 0
reservations_count = 0
users_count = 3

# clear database
def clear_db():
    print 'Clearing database'
    Location.objects.all().delete()
    Building.objects.all().delete()
    Reservation.objects.all().delete()
    Rental.objects.all().delete()
    State.objects.all().delete()
    Publisher.objects.all().delete()
    Author.objects.all().delete()
    BookCopy.objects.all().delete()
    Book.objects.all().delete()
    Book.objects.all()
    Phone.objects.all().delete()
    PhoneType.objects.all().delete()
    CostCenter.objects.all().delete()
    Category.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.all().delete()
    Configuration.objects.all().delete()
    ConfigurationValueType.objects.all().delete()


def get_random_date():
    return datetime(randint(1990,2010), randint(1,12), randint(1,28),
                    randint(0,23),      randint(0,59), randint(0,59))

def get_random_string(min_len, max_len):
    ''' Returns alpha string s, that  min_len <= len(s) < max_len. '''
    return u''.join([ choice('qwertyuiopasdfghjklzxcvbnm')
                      for i in range(0, randint(min_len, max_len)) ])

def get_random_text(max_len):
    text = [ get_random_string(1, 6) for i in range(max_len) ]
    return ' '.join(text).capitalize()[:max_len]


# categories
cat_names = ['Horror', 'History', 'Sci-Fi', 'Fantasy', 'Thriller', 'Comics']
shuffle(cat_names)
categories = []
def add_categories():
    global categories
    print 'Adding categories'
    categories = [Category(name=cat_name) for cat_name in cat_names]
    for c in categories:
        c.save()


# buildings
buil_names = [ 'Building A', 'Building B', 'Store', 'Skyscraper' ]
builds = []
def add_buildings():
    global builds
    print 'Adding %d buildings' % buildings_count
    builds = [ Building(name = buil_names[i]) for i in range(buildings_count) ]
    shuffle(builds)
    for b in builds:
        b.save()


# locations
loc_names = [ 'Room %d' % i for i in range(1,10) ]
loc_names += [ get_random_text(8).capitalize() for i in range(len(loc_names), locations_count) ]
loc_remarks = ['', 'W remoncie', 'Chwilowo zamknięta z powodu rozlania soku malinowego', 'Klucz na portierni A', 'Kto ma klucz?']
locs = []
def add_locations():
    global locs
    print 'Adding %d locations' % locations_count
    locs = [ Location(details = loc_names[i],
                      building = choice(builds),
                      remarks = choice(loc_remarks))
             for i in range(locations_count) ]
    shuffle(locs)
    for loc in locs:
        loc.save()


# publishers
publishers = []
def add_publishers():
    global publishers
    print 'Adding %d publishers' % publishers_count
    publishers = [
        Publisher(name=u"Atlas Press"),
        Publisher(name=u"Book Works"),
        Publisher(name=u"City Lights Publishers"),
        Publisher(name=u"Firebrand Books"),
        Publisher(name=u"Holland Park Press"),
        Publisher(name=u"Indiana University Press"),
        Publisher(name=u"Medknow Publications"),
        Publisher(name=u"MIT Press"),
        Publisher(name=u"Penguin Books UK"),
        ]
    publishers += [ Publisher(name = get_random_text(15).upper())
                    for i in range(len(publishers),publishers_count) ]
    for publisher in publishers:
        publisher.save()


# authors
authors = []
def add_authors():
    global authors
    print 'Adding %d authors' % authors_count
    author_names = [u'Adam Mickiewicz', u'Heniu Sienkiewicz', u'Stanisław Lem', u'Maria Konopnicka', u'Jan Brzechwa', u'Julian Tuwim', u'Ignacy Krasicki', u'Borys Pasternak', u'Horacy', u'Zbyniu Herbert', u'Marc Abrahams', u'Elizabeth Adler', u'Khadija al-Salami', u'Mitch Albom', u'John Naish', u'Zofia Nałkowska', u'Jenny Nimmo', u'Carlos Eire', u'Barbara Ann Barnett', u'Joanna Czerniawska-Far', u'Hans i Michael Eysenck']
    author_names += [ (get_random_string(4,10) + ' ' + get_random_string(6,12)).title()
                      for i in range(len(author_names),authors_count) ]   # fill up to limit
    authors = [ Author(name = author_names[i])
                for i in range(authors_count) ]
    shuffle(author_names)
    for author in authors:
        author.save()


# states
states = []
def add_states():
    global states
    print 'Adding %d states' % states_count
    states = [
        State(name="OK", is_available=True, is_visible=True),
        State(name="Bought & Arrived", is_available=True, is_visible=True),
        State(name="Lost", is_available=False, is_visible=True),
        ]
    for state in states:
        state.save()


# cost centers
cost_centers = []
def add_cc():
    global cost_centers
    print 'Adding %d cost centers' % cost_centers_count
    cost_centers_names = ['Good deal', 'Profit']
    cost_centers_names += [ get_random_text(15) for i in range(len(cost_centers_names), cost_centers_count) ]  # fill up to cost_centers_count
    shuffle(cost_centers_names)
    for i in range(cost_centers_count):
        cost_centers.append(CostCenter(name=cost_centers_names[i]))
        cost_centers[-1].save()


# books
books = []
def add_books():
    global books
    print 'Adding %d books' % books_count
    book_titles = [u'Ogniem i mieczem', u'Księga robotów', u'Bomba megabitowa', u'Liryki lozeńskie', u'Na marne', u'Qua Vadis', u'Krzyżacy', u'W pustyni i w puszczy', u'Latarnik', 'Potop', u'Sonety krymskie', u'Pan Tadeusz', u'100 bajeczek kołysaneczek', u'Bajka o szczęściu', u'Czerwony kapturek', u'Żółw i zając', u'Tajemnicza ścieżka', u'Tomcio Paluch']
    book_titles += [ get_random_text(10) for i in range(len(book_titles), books_count) ]  # fill up to books_count
    for i in range(books_count):
        book = Book(title = book_titles[i])
        book.save()        # see: http://www.djangoproject.com/documentation/models/many_to_many/#sample-usage
        for author in set([ choice(authors) for i in range(1, 5) ]):
            book.author.add(author)
        for category in set([ choice(categories) for i in range(1, 5) ]):
            book.category.add(category)
        books.append(book)
    shuffle(books)
    for book in books:
        book.save()


# copies
copies = []
def add_copies():
    global copies
    print 'Adding %d copies' % copies_count
    copies = [ BookCopy(book           = choice(books),
                        year           = randint(1900,2010),
                        state          = choice(states),
                        location       = choice(locs),
                        publisher      = choice(publishers),
                        description    = get_random_text(30),
                        publication_nr = randint(1,10),
                        cost_center    = choice(cost_centers),
                        toc            = '',
                        toc_url        = '',
                        shelf_mark     = randint(123456789,987654321),
                        )
               for i in range(copies_count) ]
    for copy in copies:
        copy.save()


# # reservations

# rsr_start_date = get_random_date()
# rsr_end_date = rsr_start_date + timedelta(days = randint(4,30))
# reservations = [ Reservation(book_copy = choice(copies),
#                              for_whom = ??,
#                              start_date = rsr_start_date,
#                              end_date = rsr_end_date,
#                              who_reserved = ??,
#                              who_cancelled = ??
#                              )
#                  for i in range(reservations_count) ]
# for reservation in reservations:
#     reservation.save()


# # rentals

# rent_start_date = get_random_date()
# rent_end_date = rent_start_date + timedelta(days = randint(5,30))
# rentals = [ Rental(reservation = ??,
#                    start_date = rent_start_date,
#                    end_date = rent_end_date,
#                    who_handed_out = ??,
#                    who_reserved = ??
#                    )
#             for i in range(rentals_count) ]
# for rental in rentals:
#     rental.save()


# code belowe can be useful when implementing reservations and rentals above

# rentals = [Rental(book=choice(books),
#                   person=choice(people),
#                   started=get_random_date(),
#                   ended=get_random_date()
#                   ) for i in xrange(rentals_count)]

# # can't return before borrowing
# for rental in rentals:
#     if rental.started > rental.ended:
#         rental.ended = None
#     rental.save()

# reservations = [ Reservation( book=choice(books),
#                               person=choice(people),
#                               starts=get_random_date(),
#                               ) for i in xrange(reservations_count) ]
# for reservation in reservations:
#     reservation.expires = reservation.starts + datetime.timedelta(days=30)
#     reservation.save()



# add telephone types
phone_types = []
def add_phone_types():
    global phone_types
    print "Adding phone types"
    phone_types = [ ('Mobile', '(\+?\d{2,3})?.?\d{3}-\d{3}-\d{3}', 'For mobiles'),
                    ('Skype', '[\d\w\-_.]+', 'Skype identifiers'),
                    ]
    for (name, re, desc) in phone_types:
        pt = PhoneType(name=name, verify_re=re, description=desc)
        pt.save()


# here we add a superuser which is available right after filling db
# src: http://docs.djangoproject.com/en/dev/topics/auth/#creating-users
# from django.contrib.auth.models import User
def add_superuser():
    user = User.objects.create_user('superadmin', 'master-over-masters@super.net', 'superadmin')
    user.first_name, user.last_name, user.is_staff, user.is_superuser = u'Superadmino', u'Superdomino', True, False
    ph = Phone(type=PhoneType.objects.all()[0], value="432-765-098")
    ph.save()
    profile = user.get_profile()
    profile.phone.add(ph)
    ph = Phone(type=PhoneType.objects.all()[0], value="superadmino.superdominko")
    ph.save()
    profile.phone.add(ph)
    profile.building = Building.objects.all()[0]
    profile.save()
    user.save()


def add_admin():
    user = User.objects.create_user('admin', 'domin@bosses.net', 'admin')
    user.first_name, user.last_name, user.is_staff, user.is_superuser = u'Admino', u'Domino', True, False
    ph = Phone(type=PhoneType.objects.all()[0], value="333-444-555")
    ph.save()
    profile = user.get_profile()
    profile.phone.add(ph)
    ph = Phone(type=PhoneType.objects.all()[0], value="admino.dominko")
    ph.save()
    profile.phone.add(ph)
    #profile.building = Building.objects.all()[0]
    profile.save()
    user.save()


def add_librarian():
    user = User.objects.create_user('lib', 'librarian@bestbook.travel', 'lib')
    user.first_name, user.last_name, user.is_staff, user.is_superuser = u'Librariano', u'Śmietano', False, False
    user.save()
    profile = user.get_profile()
    myphones = [Phone(type=PhoneType.objects.all()[0], value="200-300-400"),
                Phone(type=PhoneType.objects.all()[0], value="smietana12"),
                ]
    for p in myphones:
        p.save()
        profile.phone.add(p)
    profile.building = choice(Building.objects.all())
    profile.save()
    user.save()


def add_everyday_user():
    user = User.objects.create_user('user', 'grzegorz.brz@smigamy.com', 'user')
    user.first_name, user.last_name, user.is_staff, user.is_superuser = u'Grzegorz', u'Brzęczyszczykiewicz', False, False
    ph = Phone(type=PhoneType.objects.all()[0], value="grzesiu.brzeczy")
    ph.save()
    profile = user.get_profile()
    profile.phone.add(ph)
    profile.building = Building.objects.all()[0]
    profile.save()
    user.save()


# add users
def add_users():
    print 'Adding users'
#     add_superuser()
    add_admin()
    add_librarian()
    add_everyday_user()


# -- POPULATE GROUPS --
def populate_groups():
    from django.contrib.auth.models import Permission, Group
    # add few groups
    def readd_group(group_name, perms=[], direct_add=False):
        """
        Add permission from perms to group_name group.
        If group doesn't exist, new one is created.
        If direct_add is True, then perms is assumed to be Permission's instance. Otherwise it should be a string.
        """
        g = None
        try:
            # delete group if exist
            Group.objects.get(name=group_name).delete()
        except Group.DoesNotExist:
            pass
        # create a new one
        g = Group(name=group_name)
        g.save()
        for perm in perms:
            if direct_add or isinstance(perm, Permission):
                p = perm
            else:
                p = Permission.objects.get(codename=perm)
            assert isinstance(p, Permission)
            g.permissions.add(p)
        g.save()
    
    print "Adding app specific groups"
    from dbfiller_perms import readers_perms, admins_perms, librarians_perms
    readd_group('Readers',    perms=readers_perms, direct_add=True)
    readd_group('Librarians', perms=librarians_perms, direct_add=True)
    readd_group('Admins',     perms=admins_perms,  direct_add=True)
    
    
    # fill configuration
    print "Adding config pairs"
    from dbconfigfiller import fill_config
    config = fill_config()      # requires Group model to be filled in (because of config options validation)
    
    
    # add users to default groups
    print "Adding default user to some groups"
    from baseapp.config import Config
    config=Config()

    if len(User.objects.all()) < 1:
        add_users()
    u = User.objects.get(username='admin')
    for group_name in config.get_list('user_after_registration_groups'):
        u.groups.add(Group.objects.get(name=group_name))
        u.groups.add(Group.objects.get(name="Admins"))
    
    u = User.objects.get(username='user')
    for group_name in config.get_list('user_after_registration_groups'):
        u.groups.add(Group.objects.get(name=group_name))
    
    u = User.objects.get(username='lib')
    for group_name in config.get_list('user_after_registration_groups'):
        u.groups.add(Group.objects.get(name=group_name))
        u.groups.add(Group.objects.get(name="Librarians"))
# -- /POPULATE GROUPS --

def main():
    print '---  Running dbfiller  ---'
    clear_db()
    add_categories()
    add_buildings()
    add_locations()
    add_publishers()
    add_authors()
    add_states()
    add_cc()
    add_books()
    add_copies()
    add_phone_types()
    add_users()
    populate_groups()

