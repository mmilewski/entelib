#-*- coding=utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from entelib.baseapp.models import *
from django.template import RequestContext
from django.contrib import auth
from django.db.models import Q
from views_aux import render_forbidden, render_response, filter_query, get_book_details, reservation_status, rental_possible, rent, mark_available, render_not_implemented
from config import Config
# from django.contrib.auth.decorators import permission_required
from baseapp.forms import RegistrationForm, ProfileEditForm
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
            result_context = { 'form_content' : form }
            if extra_context is None:
                extra_context = {}
            result_context.update(extra_context)
            return render_response(request, tpl_registration_form, result_context)


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
    book_url = u'/entelib/books/%d/'
    search_data = {}                    # data of searching context
    selected_categories_ids = []        # ids of selected categories -- needed to reselect them on site reload

    if request.method == 'POST':
        post = request.POST
        search_title = post['title'].split()
        search_author = post['author'].split()
        selected_categories_ids = map(int, request.POST.getlist('category'))
        search_data.update({'title' : post['title'], 'author' : post['author'],})  # categories will be added later

        # filter with Title and/or Author
        booklist = filter_query(Book, Q(id__exact='-1'), Q(title__contains=''), [
              (search_title, 'title_any' in post, lambda x: Q(title__icontains=x)),
              (search_author, 'author_any' in post, lambda x: Q(author__name__icontains=x)),
              # (search_category, 'category_any' in post, lambda x: Q(category__id__in=x)),
            ]
        )

        # filter with Category
        if 0 not in selected_categories_ids:
            if 'category_any' in post:
                booklist = booklist.filter(category__id__in=selected_categories_ids)
            else:
                for category_id in selected_categories_ids:
                    booklist = booklist.filter(category__id=category_id)

        # compute set of categories present in booklist (= exists book which has such a category)
        # because we don't want to list categories that don't matter.
        categories_from_booklist = list(set([c for b in booklist for c in b.category.all()]))

        # put ticks on previously ticked checkboxes
        search_data.update({ 'title_any_checked' : 'true' if 'title_any' in post else '',
                             'author_any_checked' : 'true' if 'author_any' in post else '',
                             'category_any_checked' : 'true' if 'category_any' in post else '',
                             })

        # prepare each book (add url, list of authors) for rendering
        books = [{ 'title': book.title,
                   'url' : book_url % book.id,
                   'authors' : [a.name for a in book.author.all()]
                   } for book in booklist ]
    else:
        # If no POST data was sent, then we don't want to list any books, but we want
        # to fill category selection input with all possible categories.
        books = []
        categories_from_booklist = Category.objects.all()      # FIXME: can be fixed to list categories, to which at least one book belong

    # prepare categories for rendering
    search_categories = [ {'name' : '-- Any --',  'id' : 0} ]
    search_categories += [ {'name' : c.name,  'id' : c.id,  'selected': c.id in selected_categories_ids } for c in categories_from_booklist ]

    search_data.update({'categories' : search_categories,
                        })
    context = {
        'books' : books,
        'search' : search_data,
        }
    return render_response(request, 'books.html', context)



def show_book(request, book_id):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    show_url = u'/entelib/bookcopy/%d/'
    reserve_url = u'/entelib/bookcopy/%d/reserve/'
    book = Book.objects.get(id=book_id)
    book_copies = BookCopy.objects.filter(book=book_id)
    selected_locations = []
    if request.method == 'POST':
        if 'location' in request.POST:
            selected_locations = map(int, request.POST.getlist('location'))
            if 0 not in selected_locations:    # 0 in selected_locations means 'no location constraint' (= List from any location)
                book_copies = book_copies.filter(location__id__in=selected_locations)
        if r'available' in request.POST:
            if request.POST['available'] == 'available':
                book_copies = book_copies.filter(state__is_available__exact=True)
    curr_copies = []
    is_copy_reservable = request.user.has_perm('baseapp.add_reservation')
    for elem in book_copies:
        curr_copies.append({
            'url' : show_url % elem.id,
            'reserve_url' : reserve_url % elem.id,
            'location' : elem.location.name,
            'state' : elem.state.name,
            'publisher' : elem.publisher.name,
            'year' : elem.year,
            'is_available' : elem.state.is_available,
            'is_reservable' : is_copy_reservable,    # TODO: this should check if one can reserve copy and whether book is available for reserving (whatever this means)
            # 'desc_url' : '/desc_url_not_implemented',      # link generation is done in templates, see bookcopies.html
            })
    book_desc = {
        'title' : book.title,
        'authors' : [a.name for a in book.author.all()],
        'items' : curr_copies,
        'categories' : [c.name for c in book.category.all()],
        }
    search_data = {
        'locations' :
            [{'name' : '-- Any --', 'id' : 0}] + [{'name' : l.name, 'id' : l.id, 'selected': l.id in selected_locations}
                                                  for l in Location.objects.filter(id__in=[c.location.id for c in book_copies])],
        'copies_select_size': Config().get_int('copies_select_size'),      # count of elements displayed in <select> tag
        }
    return render_response(request, 'bookcopies.html', { 'book' : book_desc,
                                                         'search' : search_data,
                                                         'only_available_checked' : 'yes' if 'available' in request.POST else ''})



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
                          for u in User.objects.filter(first_name__icontains=request_first_name).filter(last_name__icontains=request_last_name).filter(email__icontains=request_email) ]
        dict = {
            'users' : user_list,
            'first_name' : request_first_name,
            'last_name' : request_last_name,
            'email' : request_email,
            }
    return render_response(request, 'users.html', dict)



def show_user(request, user_id):
    user = User.objects.get(id=user_id)
    return render_response(request, 'user.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email,
          'rentals' : 'rentals/',
          'reservations' : 'reservations/',
        }
    )


def edit_user_profile(request, profile_edit_form=ProfileEditForm):
    if not request.user.is_authenticated():
        return render_forbidden(request)

    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        form = profile_edit_form(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            new_form = profile_edit_form(user=user)
            return render_response(request, 'profile.html',
                {
                    'first_name' : user.first_name,
                    'last_name' : user.last_name,
                    'email' : user.email,
                    'rentals' : 'rentals/',
                    'reservations' : 'reservations/',
                    'form_content': new_form,
                    'edit_info': 'Edit successful',
                })
    else:
        form = profile_edit_form(user=user)

    return render_response(request, 'profile.html',
        {
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'email' : user.email,
            'rentals' : 'rentals/',
            'reservations' : 'reservations/',
            'form_content': form,
        })


def show_user_rentals(request, user_id):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    user = User.objects.get(id=user_id)
    post = request.POST
    if request.method == 'POST' and 'returned' in  post:
        returned_rental = Rental.objects.get(id=post['returned'])
        returned_rental.who_received = request.user
        returned_rental.end_date = datetime.now()
        returned_rental.save()
        mark_available(returned_rental.reservation.book_copy)
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


def show_my_rentals(request):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    user = User.objects.get(id=request.user.id)

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
        'my_rentals.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email,
          'rentals' : rent_list,
        }
    )


def show_user_reservations(request, user_id):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    user = User.objects.get(id=user_id)
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
          'cancel_all_url' : 'cancel-all/',
        }
    )


def show_my_reservations(request):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    user = User.objects.get(id=request.user.id)

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
        'my_reservations.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email,
          'reservations' : reservation_list,
          'cancel_all_url' : 'cancell-all/',
        }
    )


def reserve_for_user(request, user_id):
    return render_not_implemented(request)


def show_user_reservation(request, user_id):
    return render_not_implemented(request)



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


def cancel_all_user_resevations(request, user_id):
    return render_not_implemented(request)
