# -*- coding: utf-8 -*-

from views_aux import get_book_details, book_copy_status
from entelib.baseapp.models import Reservation, Rental, BookCopy, Book, User
from datetime import date, datetime
from django.http import HttpResponse
import csv


def generate_csv(report_type, from_date, to_date):
    '''
    Desc:
        Returns csv file in HTTP response.

    Args:
        report_type - type of the report
        from_date, to_date - describe the time period for the report

    Return:
        csv file in HTTP response.
    '''

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    writer = csv.writer(response)

    report_data = get_report_data(report_type, from_date, to_date)
    if report_data['error']:
        writer.writerow([u'Error - probably bad date format'.encode('utf8')])
        return response

    if report_type == u'status' or report_type == u'lost_books':
        writer.writerow([   u'Title'.encode('utf8'),
                            u'Shelf mark'.encode('utf8'),
                            u'Location'.encode('utf8'),
                            u'Status'.encode('utf8'),
                            u'Last time rented for'.encode('utf8'),
                            u'Last time rented on'.encode('utf8'),
                            u'Last time rented by'.encode('utf8')])
        books = report_data['report']
        for book in books:
            writer.writerow([   book['title'].encode('utf8'),
                                unicode(book['shelf_mark']).encode('utf8'),
                                book['location'].encode('utf8'),
                                book['status'].encode('utf8'),
                                book['for_whom'].encode('utf8'),
                                unicode(book['when']).encode('utf8'),
                                book['by_whom'].encode('utf8') ])

    elif report_type == u'most_often_rented':
        if from_date == u'' or to_date == u'':
            writer.writerow([u'Title'.encode('utf8'), u'Number of rentals'.encode('utf8')])
        else:
            writer.writerow([u'Title'.encode('utf8'), (u'Number of rentals from ' + from_date + u' to ' + to_date).encode('utf8')])
        books = report_data['report']
        for book in books:
            writer.writerow([ book['title'].encode('utf8'), unicode(book['num_of_rentals']).encode('utf8') ])

    elif report_type == u'most_often_reserved':
        if from_date == u'' or to_date == u'':
            writer.writerow([u'Title'.encode('utf8'), u'Number of reservations'.encode('utf8')])
        else:
            writer.writerow([u'Title'.encode('utf8'), (u'Number of reservations from ' + from_date + u' to ' + to_date).encode('utf8')])
        books = report_data['report']
        for book in books:
            writer.writerow([ book['title'].encode('utf8'), unicode(book['num_of_reservations']).encode('utf8') ])

    elif report_type == u'black_list':
        if from_date == u'' or to_date == u'':
            writer.writerow([u'Name'.encode('utf8'), u'Number of cancels'.encode('utf8')])
        else:
            writer.writerow([u'Name'.encode('utf8'), (u'Number of cancels from ' + from_date + u' to ' + to_date).encode('utf8')])
        users = report_data['report']
        for user in users:
            writer.writerow([ user['name'].encode('utf8'), unicode(user['num_of_cancels']).encode('utf8') ])

    return response


def get_report_data(report_type, from_date, to_date):
    '''
    Desc:
        Returns data for creating selected report.

    Args:
        report_type - type of the report
        from_date, to_date - describe the time period for the report

    Return:
        List describing the report, template name, info on encountered errors.
    '''

    if report_type == u'status':
        book_infos = []
        books = BookCopy.objects.all().order_by('book__title')
        last_rentals = {}
        rentals = Rental.objects.all()

        for rental in rentals:
            book_copy_id = rental.reservation.book_copy.id
            start_date = rental.start_date
            if book_copy_id not in last_rentals:
                last_rentals.update({book_copy_id: {  'when': start_date,
                                                    'for_whom': rental.reservation.for_whom.first_name + u' ' +
                                                                rental.reservation.for_whom.last_name,
                                                    'by_whom':  rental.who_handed_out.first_name + u' ' +
                                                                rental.who_handed_out.last_name}})
            elif last_rentals[book_copy_id]['when'] < start_date:
                last_rentals.update({book_copy_id: {  'when': start_date,
                                                    'for_whom': rental.reservation.for_whom.first_name + u' ' +
                                                                rental.reservation.for_whom.last_name,
                                                    'by_whom':  rental.who_handed_out.first_name + u' ' +
                                                                rental.who_handed_out.last_name}})

        for book in books:
            book_details = get_book_details(book)
            if book.id not in last_rentals:
                not_rented_yet = True
            else:
                not_rented_yet = False

            if not_rented_yet:
                for_whom = when = by_whom = u'Not rented yet'
            else:
                last_rental = last_rentals[book.id]
                (for_whom, when, by_whom) = (last_rental['for_whom'], last_rental['when'].date(), last_rental['by_whom'])

            title = book_details['title']
            shelf_mark = book_details['shelf_mark']
            location = book_details['location']

            status = book_copy_status(book)
            if isinstance(status, int):
                status = u'Rentable'

            book_infos.append({ 'title': title,
                                'shelf_mark': shelf_mark,
                                'location': location,
                                'status': status,
                                'for_whom': for_whom,
                                'when': when,
                                'by_whom': by_whom,
                                'not_rented_yet': not_rented_yet})

        return {'report': book_infos, 'template': 'library_status.html', 'error': False}

    ###

    elif report_type == u'most_often_rented':
        book_infos = []
        books = Book.objects.all()
        rentals = Rental.objects.all()
        date_empty = False
        nums_of_rentals = {}

        if from_date == u'' or to_date == u'':
            date_empty = True
        else:
            try:
                [y, m, d] = map(int,from_date.split('-'))
                start_date = date(y, m, d)
                [y, m, d] = map(int,to_date.split('-'))
                end_date = date(y, m, d)
            except:
                return {'error': True, 'report': [], 'template': 'reports.html'}

        for book in books:
            if book.id not in nums_of_rentals:
                nums_of_rentals.update({book.id: 0})

        for rental in rentals:
            book_id = rental.reservation.book_copy.book.id
            if date_empty:
                nums_of_rentals[book_id] += 1
            else:
                if rental.start_date.date() >= start_date and rental.start_date.date() <= end_date:
                    nums_of_rentals[book_id] += 1

        for book in books:
            book_infos.append({'title': book.title, 'num_of_rentals': nums_of_rentals[book.id]})

        return {'report': sorted(book_infos, key=lambda k: k['num_of_rentals'], reverse=True), 'template': 'most_often_rented.html', 'error': False}

    ###

    elif report_type == u'most_often_reserved':
        book_infos = []
        books = Book.objects.all()
        reservations = Reservation.objects.all()
        nums_of_reservations = {}
        date_empty = False

        if from_date == u'' or to_date == u'':
            date_empty = True
        else:
            try:
                [y, m, d] = map(int,from_date.split('-'))
                start_date = date(y, m, d)
                [y, m, d] = map(int,to_date.split('-'))
                end_date = date(y, m, d)
            except:
                return {'error': True, 'report': [], 'template': 'reports.html'}

        for book in books:
            if book.id not in nums_of_reservations:
                nums_of_reservations.update({book.id: 0})

        for reservation in reservations:
            book_id = reservation.book_copy.book.id
            if date_empty:
                nums_of_reservations[book_id] += 1
            else:
                if reservation.start_date >= start_date and reservation.start_date <= end_date:
                    nums_of_reservations[book_id] += 1

        for book in books:
            book_infos.append({'title': book.title, 'num_of_reservations': nums_of_reservations[book.id]})

        return {'report': sorted(book_infos, key=lambda k: k['num_of_reservations'], reverse=True), 'template': 'most_often_reserved.html', 'error': False}

    ###

    elif report_type == u'black_list':
        nums_of_cancels = {}
        user_infos = []
        users = User.objects.all()
        reservations = Reservation.objects.filter(who_cancelled__isnull=False)
        date_empty = False

        if from_date == u'' or to_date == u'':
            date_empty = True
        else:
            try:
                [y, m, d] = map(int,from_date.split('-'))
                start_date = date(y, m, d)
                [y, m, d] = map(int,to_date.split('-'))
                end_date = date(y, m, d)
            except:
                return {'error': True, 'report': [], 'template': 'reports.html'}

        for user in users:
            if user.id not in nums_of_cancels:
                nums_of_cancels.update({user.id: 0})

        for reservation in reservations:
            user_id = reservation.for_whom.id
            if date_empty:
                nums_of_cancels[user_id] += 1
            else:
                if reservation.start_date >= start_date and reservation.start_date <= end_date:
                    nums_of_cancels[user_id] += 1

        for user in users:
            user_infos.append({'name': user.first_name + u' ' + user.last_name, 'num_of_cancels': nums_of_cancels[user.id]})

        return {'report': sorted(user_infos, key=lambda k: k['num_of_cancels'], reverse=True), 'template': 'black_list.html', 'error': False}

    ###

    elif report_type == u'lost_books':
        book_infos = get_report_data(u'status', u'', u'')['report']
        lost_books = filter(lambda b: b['status'] == 'Unavailable', book_infos)
        return {'report': lost_books, 'template': 'library_status.html', 'error': False}

    else:
        return {'report': [], 'template': 'reports.html', 'error': True}
