#-*- coding=utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from entelib.baseapp.models import *
from django.template import RequestContext
from django.contrib import auth
from django.db.models import Q
from views_aux import render_forbidden, render_response, filter_query, get_book_details, reservation_status, rental_possible, rent
from config import Config
# from django.contrib.auth.decorators import permission_required
from baseapp.forms import RegistrationForm
from datetime import date, datetime, timedelta




def register(request, action, registration_form=RegistrationForm, extra_context=None):
    '''
    Handles registration (adding new user) process.
    '''
    user = request.user
    action = action if not action.endswith('/') else action[:-1]    # cut trailing slash
    tpl_logout_first = 'registration/reg_logout_first.html'
    tpl_registration_form = 'registration/reg_form.html'

    if user.is_authenticated():
        if action in ['logout',]:
            auth.logout(request)
            return HttpResponseRedirect('/entelib/register/newuser/')
        else:
            return render_response(request, tpl_logout_first)
    else:   # not authenticated
        if action == 'newuser':
            # commit new user
            if request.method == 'POST':
                form = registration_form(data=request.POST, files=request.FILES)
                if form.is_valid():
                    new_user = form.save()
                    return HttpResponseRedirect('/entelib/')
            # display form
            else:
                form = registration_form()

            # prepare response
            if extra_context is None:
                extra_context = {}
            context = RequestContext(request)
            for key, value in extra_context.items():
                context[key] = callable(value) and value() or value
            return render_to_response(tpl_registration_form,
                                      { 'form_content' : form },
                                      context_instance=context)


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/entelib/')


def default(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/entelib/login/')
    return render_response(request, 'entelib.html')


def show_books(request):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    url = u'/entelib/books/'
    books = []
    search = {}
    dict = {}
    if request.method == 'POST':
        post = request.POST
        search_title = post['title'].split()
        search_author = post['author'].split()
        search_category = post['category'].split()
        search = {'title' : post['title'], 'author' : post['author'], 'category' : post['category'], }
        booklist = filter_query(Book, Q(id__exact='-1'), Q(title__contains=''), [
              (search_title, 'title_any' in post, lambda x: Q(title__icontains=x)),
              (search_author, 'author_any' in post, lambda x: Q(author__name__icontains=x)),
              # (search_category, 'category_any' in post, lambda x: q(id__something_with_category_which_is_not_yet_implemented))  # TODO
            ]
        )
        for elem in booklist:
            books.append({
                'title':elem.title,
                'url' : url + unicode(elem.id) + '/',
                'authors' : [a.name for a in elem.author.all()]
                })
        dict = {'books' : books, 'search' : search}
        dict.update({
            'title_any_checked' : 'true' if 'title_any' in post else '',
            'author_any_checked' : 'true' if 'author_any' in post else '',
            'category_any_checked' : 'true' if 'category_any' in post else '',
        })
    return render_response(request, 'books.html', dict)



def show_book(request, book_id):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    url = u'/entelib/bookcopy/'
    book = Book.objects.get(id=book_id)
    book_copies = BookCopy.objects.filter(book=book_id)
    if request.method == 'POST':
        if 'location' in request.POST:
            if not request.POST['location'] == u'0':
                book_copies = book_copies.filter(location__id__exact=request.POST['location'])
        if r'available' in request.POST:
            if request.POST['available'] == 'available':
                book_copies = book_copies.filter(state__is_available__exact=True)
    curr_copies = []
    max_desc_len = Config().get_int('truncated_description_len')
    for elem in book_copies:
        curr_copies.append({
            'url' : url + unicode(elem.id) + '/',
            'reserve_url' : url + unicode(elem.id) + '/reserve/',
            'location' : elem.location.name,
            'state' : elem.state.name,
            'publisher' : elem.publisher.name,
            'year' : elem.year,
            'desc_url' : elem.toc_url,
            })
    book_desc = {
        'title' : book.title,
        'authors' : [a.name for a in book.author.all()],
        'items' : curr_copies,
        'locations' : [{'name' : 'All', 'id' : 0}] + [{'name' : l.name, 'id' : l.id} for l in Location.objects.filter(id__in=[c.location.id for c in book_copies])]
        }
    return render_response(request, 'bookcopies.html', { 'book' : book_desc, 'only_available_checked' : 'yes' if 'available' in request.POST else ''})



def show_book_copy(request, bookcopy_id):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    book_copy = BookCopy.objects.get(id=bookcopy_id)
    book_desc = get_book_details(book_copy)
    return render_response(request, 'bookcopy.html',
        {
            'book' : book_desc,
            'can_reserve' : request.user.has_perm('baseapp.add_reservation'),
            # 'can_rent' : request.user.has_perm('baseapp.add_rental'), and  # TODO
            # 'can_return' : request.user.has_perm('baseapp.change_rental'),  # TODO
        }
    )



def show_users(request):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    dict = {}
    if request.method == 'POST':
        request_first_name = request.POST['first_name'] if 'first_name' in request.POST else ''
        request_last_name = request.POST['last_name'] if 'last_name' in request.POST else ''
        request_email = request.POST['email'] if 'email' in request.POST else ''
        user_list = []
        if 'action' in request.POST and request.POST['action'] == 'Search':
            user_list = [ {'last_name' : u.last_name, 'first_name' : u.first_name, 'email' : u.email,'url' : unicode(u.id) + u'/'}
                          for u in CustomUser.objects.filter(first_name__icontains=request_first_name).filter(last_name__icontains=request_last_name).filter(email__icontains=request_email) ]
        dict = {
            'users' : user_list,
            'first_name' : request_first_name,
            'last_name' : request_last_name,
            'email' : request_email,
            }
    return render_response(request, 'users.html', dict)



def show_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    return render_response(request, 'user.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email,
          'rentals' : 'rentals/',
          'reservations' : 'reservations/',
        }
    )


#the following is draft
def show_user_rentals(request, user_id):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    user = CustomUser.objects.get(id=user_id)
    post = request.POST
    if request.method == 'POST' and 'returned' in  post:
        returned_rental = Rental.objects.get(id=post['returned'])
        returned_rental.who_received = request.user
        returned_rental.end_date = datetime.now()
        returned_rental.save()
    user_rentals = Rental.objects.filter(reservation__for_whom=user.id).filter(who_received__isnull=True)
    rent_list = [ {'id' : r.id,
                   'shelf_mark' : r.reservation.book_copy.shelf_mark,
                   'title' : r.reservation.book_copy.book.title, 
                   'authors' : [a.name for a in r.reservation.book_copy.book.author.all()],
                   'from_date' : r.start_date,
                   'to_date' : r.reservation.end_date,
                  }
                    for r in user_rentals ]

    return render_response(request,
        'user_books.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email,
          'rentals' : rent_list,
        }
    )


def show_user_reservations(request, user_id):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        post = request.POST
        librarian = request.user
        if 'reservation_id' in post:
            rent(Reservation.objects.get(id=post['reservation_id']), librarian)

    user_reservations = Reservation.objects.filter(for_whom=user).filter(rental=None).filter(when_cancelled=None)
    reservation_list = [ {'id' : r.id,
                          'url' : unicode(r.id) + u'/',
                          'book_copy_id' : r.book_copy.id,
                          'shelf_mark' : r.book_copy.shelf_mark,
                          'rental_impossible' : '' if rental_possible(r) else reservation_status(r),
                          'title' : r.book_copy.book.title,
                          'authors' : [a.name for a in r.book_copy.book.author.all()],
                          'from_date' : r.start_date,
                         } for r in user_reservations]
    return render_response(request,
        'user_reservations.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email,
          'reservations' : reservation_list,
          'cancel_all_url' : 'cancell-all/',
        }
    )


def reserve_for_user(request, user):
    user = CustomUser.objects.get(id=user)


def show_user_reservation(request, user_id):
    pass



'''
def users_rental(request, user_id, rental_id):
    user = User.objects.get(id=user_id)
    rental = Rental.objects.get(id=rental_
'''


def reserve(request, copy):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.add_reservation'):
        return render_forbidden(request)
    book_copy = BookCopy.objects.get(id=copy)
    book_desc = get_book_details(book_copy)
    reserved = {}
    post = request.POST
    if request.method == 'POST':
        r = Reservation(who_reserved=request.user, book_copy=book_copy, for_whom=request.user)
        if 'from' in post and post['from'] != u'':
            try:
                [y, m, d] = map(int,post['from'].split('-'))
                r.start_date = date(y, m, d)
                r.save()
                reserved.update({'ok' : 'ok'})
                reserved.update({'from' : post['from']})
            except:
                reserved.update({'error' : 'error'})
        elif 'action' in post and post['action'] == 'reserve':
            r.start_date = date.today()
            r.save()
            reserved.update({'from' : r.start_date.isoformat()})
            reserved.update({'ok' : 'ok'})


    return render_response(request, 'reserve.html',
        {
            'book' : book_desc,
            'reserved' : reserved,
            'can_reserve' : request.user.has_perm('baseapp.add_reservation') and book_copy.state.is_visible,
        }
    )
