#-*- coding=utf-8 -*- 
import random
import datetime
from entelib.baseapp.models import *

NR_OF_BOOKS = 30
NR_OF_USERS = 30
NR_OF_RENTALS = 300
NR_OF_RESERVATIONS = 500

people = [Person(info=u'Some info on person %d\n' % i) for i in xrange(1,NR_OF_USERS)]
for person in people: person.save()

books_authors = [u'Okasaki, Chris', u'Chandler, Raymond', u'Cormen', u'Sysło, M']
books_titles = [u'Good book', u'Ilustrowana encyklopedia wszystkiego', u'Ratatuille', u'Theory of plot']

books = [Book(title=random.choice(books_titles), 
              author=random.choice(books_authors), 
              localization=u'Where is book nr %d? Check room %d.' % (i, random.randint(1,300)),
              status=random.choice([u'a', u'd'])) for i in xrange(1,NR_OF_BOOKS)
        ]
for book in books: book.save()

def randdate():
    return datetime.datetime(random.randint(1990,2009),
                                random.randint(1,12),
                                random.randint(1,28),
                                random.randint(0,23),
                                random.randint(0,59),
                                random.randint(0,59))


rentals = [Rental(book=random.choice(books),
                  person=random.choice(people),
                  started=randdate(),
                  ended = randdate() 
                  ) for i in xrange(NR_OF_RENTALS)]


# can't return before borrowing
for rental in rentals:
    if rental.started > rental.ended:
        rental.ended = None
    rental.save()


reservations = [Reservation(book=random.choice(books),
                  person=random.choice(people),
                  starts=randdate(),
                  ) for i in xrange(NR_OF_RESERVATIONS)]
for reservation in reservations: 
    reservation.expires = reservation.starts + datetime.timedelta(days=30)
    reservation.save()
