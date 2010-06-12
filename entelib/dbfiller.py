#-*- coding=utf-8 -*-
print '---  Running dbfiller  ---'

#
# TODO:
#  - pictures generating
#  - rentals generating
#  - reservations generating


from random import randint, choice, shuffle
from datetime import datetime, timedelta
from baseapp.models import *
from django.contrib.auth.models import Group

# clear database
print 'Clearing database'
Location.objects.all().delete()
Building.objects.all().delete()
Reservation.objects.all().delete()
Rental.objects.all().delete()
Picture.objects.all().delete()
State.objects.all().delete()
Publisher.objects.all().delete()
Author.objects.all().delete()
BookCopy.objects.all().delete()
Book.objects.all().delete()
Phone.objects.all().delete()
PhoneType.objects.all().delete()
CostCenter.objects.all().delete()
Category.objects.all().delete()
UserProfile.objects.all().delete()
User.objects.all().delete()

# NOTE: Users are not deleted. Only admin is.


# define number of records to create
locations_count = 8
buildings_count = 4
authors_count = 25
pictures_count = 3
publishers_count = 7
books_count = 11
states_count = 3
copies_count = 51
cost_centers_count = 2
rentals_count = 30
reservations_count = 50
users_count = 50


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
print 'Adding categories'
cat_names = ['Horror', 'History', 'Sci-Fi', 'Fantasy']
shuffle(cat_names)
for cat_name in cat_names:
    Category(name=cat_name).save()


# buildings
print 'Adding %d buildings' % buildings_count
buil_names = [ 'Building A', 'Building B', 'Store', 'Skyscraper' ]
builds = [ Building(name = buil_names[i]) for i in range(buildings_count) ]
shuffle(builds)
for b in builds:
    b.save()


# locations
print 'Adding %d locations' % locations_count
loc_names = [ 'Room %d' % i for i in range(1,10) ]
loc_names += [ get_random_text(8).capitalize() for i in range(len(loc_names), locations_count) ]
loc_remarks = ['', 'W remoncie', 'Chwilowo zamknięta z powodu rozlania soku malinowego', 'Klucz na portierni A', 'Kto ma klucz?']
locs = [ Location(details = loc_names[i],
                  building = choice(builds),
                  remarks = choice(loc_remarks))
         for i in range(locations_count) ]
shuffle(locs)
for loc in locs:
    loc.save()


# publishers
print 'Adding %d publishers' % publishers_count
publishers = [ Publisher(name = get_random_text(15).upper())
               for i in range(publishers_count) ]
for publisher in publishers:
    publisher.save()


# authors
print 'Adding %d authors' % authors_count
author_names = [u'Adam Mickiewicz', u'Heniu Sienkiewicz', u'Stanisław Lem']
author_names += [ (get_random_string(4,10) + ' ' + get_random_string(6,12)).title()
                  for i in range(len(author_names),authors_count) ]   # fill up to limit
authors = [ Author(name = author_names[i])
            for i in range(authors_count) ]
shuffle(author_names)
for author in authors:
    author.save()


# # pictures

#
# TODO: implement
#
# picture_descs = [ get_random_text(40) for i in range(pictures_count) ]
# picture_files = [ ]  # ??
# pictures = [ Picture(description = picture_descs[i]
#                      file = picture_files[i] )
#              for i in range(pictures_count) ]
# for picture in pictures:
#     picture.save()


# states
print 'Adding %d states' % states_count
state_names = [ get_random_string(3,7) for i in range(states_count) ]
state_availability = [ True, False ]
states = [ State(name = state_names[i],
                 is_available = choice(state_availability))
           for i in range(states_count) ]
for state in states:
    state.save()


# cost centers
print 'Adding %d cost centers' % cost_centers_count
cost_centers_names = ['Good deal', 'Profit']
cost_centers_names += [ get_random_text(15) for i in range(len(cost_centers_names), cost_centers_count) ]  # fill up to cost_centers_count
shuffle(cost_centers_names)
cost_centers = []
for i in range(cost_centers_count):
    cost_centers.append(CostCenter(name=cost_centers_names[i]))
    cost_centers[-1].save()


# books
print 'Adding %d books' % books_count
book_titles = [u'Ogniem i mieczem', u'Księga robotów', u'Bomba megabitowa', u'Liryki lozeńskie']
book_titles += [ get_random_text(10) for i in range(len(book_titles), books_count) ]  # fill up to books_count
books = []
for i in range(books_count):
    book = Book(title = book_titles[i])
    book.save()        # see: http://www.djangoproject.com/documentation/models/many_to_many/#sample-usage
    for author in set([ choice(authors) for i in range(1, 5) ]):
        book.author.add(author)
    books.append(book)
shuffle(books)
for book in books:
    book.save()


# copies
print 'Adding %d copies' % copies_count
copies = [ BookCopy(book           = choice(books),
                    year           = randint(1900,2010),
                    state          = choice(states),
                    location       = choice(locs),
                    publisher      = choice(publishers),
                    # picture        = choice(pictures),
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
print "Adding phone types"
phone_types = [ ('Mobile', '(\+?\d{2,3})?.?\d{3}-\d{3}-\d{3}', 'For mobiles'),
                ('Skype', '[\d\w\-_.]+', 'Skype identifiers'),
                ('Morse decoder', '', ''),
                ]
for (name, re, desc) in phone_types:
    pt = PhoneType(name=name, verify_re=re, description=desc)
    pt.save()


# here we add a superuser which is available right after filling db
# src: http://docs.djangoproject.com/en/dev/topics/auth/#creating-users
# from django.contrib.auth.models import User

print "Adding users"
# from entelib.baseapp.models import CustomUser
# superuser
user = User.objects.create_user('admin', 'iam@superfrog.com', 'admin')
user.first_name, user.last_name, user.is_staff, user.is_superuser = u'Admino', u'Domino', True, True
# user.save()
ph = Phone(type=PhoneType.objects.get(id=1), value="333-444-555")
ph.save()
user.get_profile().phone.add(ph)
ph = Phone(type=PhoneType.objects.get(id=2), value="admino.dominko")
ph.save()
user.get_profile().phone.add(ph)
user.save()
# everyday user
user = User.objects.create_user('user', 'iam@frog.com', 'user')
user.first_name, user.last_name, user.is_staff, user.is_superuser = u'Grzegorz', u'Brzęczyszczykiewicz', False, False
ph = Phone(type=PhoneType.objects.get(id=2), value="grzesiu.brzeczy")
ph.save()
user.get_profile().phone.add(ph)
user.save()


# add few groups
def readd_group(group_name, perms=[]):
    '''
    Add permission from perms to group_name group.
    If group doesn't exist, new one is created.
    '''
    g = None
    try:
        # read group from db
        g = Group.objects.get(name=group_name)
    except:
        # or create a new one
        g = Group(name=group_name)
        g.save()
    for perm in perms:
        p = Permission.objects.get(codename=perm)
        g.permissions.add(p)
    g.save()

print "Adding app specific groups"
readd_group('Readers', perms=['list_books', 'view_own_profile', 'add_reservation', 'add_bookrequest',])  # TODO: fill permissions
readd_group('VIPs', perms=['list_reports', 'list_users', ])


from dbconfigfiller import fill_config

print "Adding config pairs"
config = fill_config()

# add user
print "Adding default user to some groups"
u = User.objects.get(username='user')
for group_name in config.get_list('user_after_registration_groups'):
    print group_name
    u.groups.add(Group.objects.get(name=group_name))
