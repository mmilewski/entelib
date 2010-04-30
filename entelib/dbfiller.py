#-*- coding=utf-8 -*- 

#
# TODO:
#  - pictures generating
#  - rentals generating
#  - reservations generating


from random import randint, choice, shuffle
from datetime import datetime, timedelta
from entelib.baseapp.models import *

# clear database
Location.objects.all().delete()
Reservation.objects.all().delete()
Rental.objects.all().delete()
Picture.objects.all().delete()
State.objects.all().delete()
Publisher.objects.all().delete()
Author.objects.all().delete()
BookCopy.objects.all().delete()
Book.objects.all().delete()
# NOTE: Users are not deleted. Only admin is.


# define number of records to create
locations_count = 8
authors_count = 25
pictures_count = 3
publishers_count = 7
books_count = 21
states_count = 3
copies_count = 101
rentals_count = 30
reservations_count = 50
users_count = 50


def get_random_date():
    return datetime.datetime(randint(1990,2010), randint(1,12), randint(1,28),
                             randint(0,23),      randint(0,59), randint(0,59))

def get_random_string(min_len, max_len):
    ''' Returns alpha string s, that  min_len <= len(s) < max_len. '''
    return u''.join( [choice('qwertyuiopasdfghjklzxcvbnm') for i in range(0, randint(min_len, max_len))] )

def get_random_text(max_len):
    text = [ get_random_string(1, 8) for i in range(max_len) ]
    return ' '.join(text).capitalize()[:max_len]


# locations
loc_names = ['Budynek A', 'Budynek B', 'Namiot', 'Szafa w przedpokoju', 'Półka specjalna']
loc_names += [ get_random_text(18).capitalize() for i in range(len(loc_names), locations_count) ]
loc_remarks = ['', 'W remoncie', 'Chwilowo niedostępna z powodu rozlania soku malinowego', 'Klucz na portierni A', 'Kto ma klusz?']
locs = [ Location(name = loc_names[i],
                  remarks = choice(loc_remarks))
         for i in range(locations_count) ]
shuffle(locs)
for loc in locs:
    loc.save()


# publishers
publishers = [ Publisher(name = get_random_text(15).upper())
               for i in range(publishers_count) ]
for publisher in publishers:
    publisher.save()


# authors
author_names = [u'Adam Mickiewicz', u'Heniu Sienkiewicz', u'Stanisław Lem']
author_names += [ (get_random_string(4,10) + ' ' + get_random_string(6,12)).title()
                  for i in range(len(author_names),authors_count) ]  # fill up to limit
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
state_names = [ get_random_string(7,20) for i in range(states_count) ]
state_availability = [ True, False ]
states = [ State(name = state_names[i],
                 is_available = choice(state_availability))
           for i in range(states_count) ]
for state in states:
    state.save()


# books
book_titles = [u'Ogniem i mieczem', u'Księga robotów', u'Bomba megabitowa', u'Liryki lozeńskie']
book_titles += [ get_random_text(30) for i in range(len(book_titles), books_count) ]  # fill up to books_count
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
copies = [ BookCopy(book           = choice(books),
                    year           = randint(1900,2010),
                    state          = choice(states),
                    location       = choice(locs),
                    publisher      = choice(publishers),
                    # picture        = choice(pictures),
                    description    = get_random_text(300),
                    publication_nr = randint(1,10),
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



# here we add a superuser which is available right after filling db
# src: http://docs.djangoproject.com/en/dev/topics/auth/#creating-users
# from django.contrib.auth.models import User
from entelib.baseapp.models import CustomUser

extra_user_name = 'admin'
try:
    user = CustomUser.objects.get(username=extra_user_name)  # get may throw DoesNotExist
    user.delete()
except:
    pass
user = CustomUser.objects.create_user(extra_user_name, 'iam@frog.com', 'admin')
user.first_name, user.last_name = 'Admino', 'Domino'
user.is_staff = True
user.is_superuser = True
user.save()
