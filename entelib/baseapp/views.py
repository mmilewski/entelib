# -*- coding: utf-8 -*-
# TODO: poprawic sprawdzanie uprawnien na poczatku widokow

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from entelib.baseapp.models import *
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import Group
from django.db.models import Q
from views_aux import render_forbidden, render_response, filter_query, get_book_details, get_phones_for_user, reservation_status, is_reservation_rentable, rent, mark_available, render_not_implemented, render_not_found, is_book_copy_rentable, get_locations_for_book, Q_reservation_active, cancel_reservation, when_copy_reserved
import baseapp.views_aux as aux
import baseapp.emails as mail
from reports import get_report_data, generate_csv
from entelib import settings
from config import Config
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.admin.views.decorators import staff_member_required
from baseapp.forms import RegistrationForm, ProfileEditForm, BookRequestForm, ConfigOptionEditForm
from datetime import date, datetime, timedelta


config = Config()


@login_required
@permission_required('baseapp.load_default_config')
def load_default_config(request, do_it=False):
    '''
    Restores default values to config. This is rather for developement than production usage.
    '''
    if do_it:
        from dbconfigfiller import fill_config
        fill_config()
    return render_response(request, 'load_default_config.html', {})


@login_required
@permission_required('baseapp.list_config_options')
def show_config_options(request):
    '''
    Handles listing config options from Configuration model (also Config class).
    '''
    template = 'config/list.html'
    config = Config(user=request.user)
    opts = config.get_all_options().values()
    lex_by_key = lambda a,b : -1 if a.key < b.key else (1 if a.key > b.key else 0)
    opts.sort(cmp=lex_by_key)
    context = {
        'options' : opts,
        }
    return render_response(request, template, context)


@login_required
@permission_required('baseapp.edit_option')
def edit_config_option(request, option_key, edit_form=ConfigOptionEditForm):
    '''
    Handles editing config option by user.
    '''
    user = request.user

    tpl_edit_option = 'config/edit_option.html'
    context = {}
    config = Config(user)
    if option_key not in config:
        return render_not_found(request, item_name='Config option')

    form_initial = {'value': config[option_key]}
    # redisplay form
    if request.method == 'POST':
        form = edit_form(user=user, option_key=option_key, data=request.POST, initial=form_initial)
        if form.is_valid():
            form.save()
            return render_response(request, tpl_edit_option, context)
    # display fresh new form
    else:
        form = edit_form(user=user, option_key=option_key, initial=form_initial)

    form.option_key = option_key
    form.description = config.get_description(option_key)
    form.can_override = config.can_override(option_key)
    context['form'] = form
    return render_response(request, tpl_edit_option, context)

    
@login_required
@permission_required('baseapp.list_emaillog')
def show_email_log(request):
    '''
    Handles listing all emails (logged messages, not adresses).
    '''
    template = 'email/list.html'
    context = {
        'emails' : EmailLog.objects.all().order_by('-sent_date'),
        }

    return render_response(request, template, context)


@login_required
@permission_required('baseapp.add_bookrequest')
def request_book(request, request_form=BookRequestForm):
    '''
    Handles requesting for book by any user.
    '''
    user = request.user
    # if not all([user.is_authenticated(), user.has_perm('baseapp.add_bookrequest')]):
    #     return render_forbidden(request)

    template = 'book_request.html'
    context = {}

    # redisplay form
    if request.method == 'POST':
        form = request_form(user=user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            context['show_confirmation_msg'] = True
            context['requested_items'] = BookRequest.objects.all()
            return render_response(request, template, context)
    # display fresh new form
    else:
        form = request_form(user=user)

    context['form_content'] = form
    context['books'] = Book.objects.all()
    return render_response(request, template, context)


def register(request, action, registration_form=RegistrationForm, extra_context={}):
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
            result_context.update(extra_context)
            return render_response(request, tpl_registration_form, result_context)
        else:  # action other than newuser
            return HttpResponseRedirect('/entelib/register/newuser/')


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/entelib/')


@login_required
def default(request):
    return render_response(request, 'entelib.html')


@login_required
def show_books(request, non_standard_user_id=False):
    '''
Desc:
    Allows to find, and lists searched books.

Args:
    non_standard_user_id is used when librarian is searching for a book in the name of user.
    In that case non_standard_user_id is most likely different than request.user
    '''
    # data for the template
    book_url = u'/entelib/books/%d/'    # where you go after clicking "search" button
    if non_standard_user_id is not False:  # and where you go if there is a non std user given
        book_url = u'/entelib/users/%d/reservations/new/book/%s/' % (non_standard_user_id, '%d')
    config.set_user(request.user)
    search_data = {}                    # data of searching context
    selected_categories_ids = []        # ids of selected categories -- needed to reselect them on site reload

    # if POST is sent we need to take care of some things
    if request.method == 'POST':
        post = request.POST
        search_title = post['title'].split()
        search_author = post['author'].split()
        selected_categories_ids = map(int, request.POST.getlist('category'))
        search_data.update({'title' : post['title'], 'author' : post['author'],})  # categories and checkboxes will be added later

        # filter with Title and/or Author
        booklist = aux.filter_query(Book, Q(id__exact='-1'), [
              (search_title, 'title_any' in post, lambda x: Q(title__icontains=x)),
              (search_author, 'author_any' in post, lambda x: Q(author__name__icontains=x)),
            ]
        )

        # filter with Category
        if selected_categories_ids and (0 not in selected_categories_ids):  # at least one 'real' category selected
            if 'category_any' in post:
                booklist = booklist.filter(category__id__in=selected_categories_ids)
            else:
                for category_id in selected_categories_ids:
                    booklist = booklist.filter(category__id=category_id)

        if config.get_bool('cut_categories_list_to_found_books'):
            # compute set of categories present in booklist (= exists book which has such a category)
            categories_from_booklist = list(set([c for b in booklist for c in b.category.all()]))
        else:
            # list all nonempty categories
            categories_from_booklist = list(set([c for b in Book.objects.only('category').all() for c in b.category.all()]))

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
        if config.get_bool('list_only_existing_categories_in_search'):
            categories_from_booklist = list(set([c for b in Book.objects.all() for c in b.category.all()]))
        else:
            categories_from_booklist = Category.objects.all()      # FIXME: can be fixed to list categories, to which at least one book belong
                                                                   # I wouldn't do that - mbr

    # prepare categories for rendering
    search_categories  = [ {'name' : '-- Any --',  'id' : 0} ]
    search_categories += [ {'name' : c.name,  'id' : c.id,  'selected': c.id in selected_categories_ids }  for c in categories_from_booklist ]

    # update search context
    search_data.update({'categories' : search_categories,
                        'categories_select_size' : min(len(search_categories), config.get_int('categories_select_size')),
                        })

    for_whom = aux.user_full_name(non_standard_user_id)

    context = {
        'for_whom' : for_whom,
        'books' : books,
        'search' : search_data,
        'can_add_book' : request.user.has_perm('baseapp.add_book'),
        }
    return render_response(request, 'books.html', context)


@login_required
def show_book(request, book_id, non_standard_user_id=False):
    config = Config()
    # if we have a non_standard_user we treat him special
    url_for_non_standard_users = u'/entelib/users/%d/reservations/new/bookcopy/%s/' % (non_standard_user_id, u'%d')
    show_url = u'/entelib/bookcopy/%d/' if non_standard_user_id == False else url_for_non_standard_users
    reserve_url = u'/entelib/bookcopy/%d/reserve/' if non_standard_user_id == False else url_for_non_standard_users
    # do we have such book?
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return render_not_found(request, item_name='Book')
    # find all visible copies of given book
    book_copies = BookCopy.objects.filter(book=book_id).filter(state__is_visible=True)
    selected_locations = []
    if request.method == 'POST':
        # satisfy the location constraint:
        if 'location' in request.POST:
            selected_locations = map(int, request.POST.getlist('location'))
            if 0 not in selected_locations:    # 0 in selected_locations means 'no location constraint' (= List from any location)
                book_copies = book_copies.filter(location__id__in=selected_locations)
        # satisfy the availability constraint:
        if 'available' in request.POST:
            if request.POST['available'] == 'available':
                book_copies = book_copies.filter(state__is_available__exact=True)
    curr_copies = []
    is_copy_reservable = request.user.has_perm('baseapp.add_reservation')
    # create list of dicts of book_copies
    for elem in book_copies:
        curr_copies.append({
            'url'           : show_url % elem.id,
            'reserve_url'   : reserve_url % elem.id,
            'shelf_mark'    : elem.shelf_mark,
            'location'      : elem.location,
            'state'         : elem.state,
            'publisher'     : elem.publisher,
            'year'          : elem.year,
            'is_available'  : elem.state.is_available,
            'is_reservable' : is_copy_reservable,    # it allows reserving in template - true if user is allowed to reserve
            'when_reserved' : when_copy_reserved(elem),
            })
    # dict for book
    book_desc = {
        'id'          : book.id,
        'title'       : book.title,
        'authors'     : [a.name for a in book.author.all()],
        'items'       : curr_copies,
        'categories'  : [c.name for c in book.category.all()],
        }
    search_locations  = [{'name' : '-- Any --', 'id' : 0}]
    search_locations += [{'name' : unicode(l), 'id' : l.id, 'selected': l.id in selected_locations}  for l in get_locations_for_book(book.id)]
    search_data = {
        'locations' : search_locations,
        'copies_location_select_size': min(len(search_locations), config.get_int('copies_location_select_size')),      # count of elements displayed in <select> tag
        }

    for_whom = aux.user_full_name(non_standard_user_id)

    last_date = date.today() + timedelta(config.get_int('when_reserved_period'))

    return render_response(request, 'bookcopies.html', { 'book' : book_desc,
                                                         'last_date': last_date,
                                                         'search' : search_data,
                                                         'for_whom' : for_whom,
                                                         'can_add_bookcopy' : request.user.has_perm('baseapp.add_bookcopy'),
                                                         'only_available_checked' : 'yes' if 'available' in request.POST else '',
                                                         'time_bar': config.get_bool('enable_time_bar')})


@login_required
def show_book_copy(request, bookcopy_id):
    try:
        book_copy = BookCopy.objects.get(id=bookcopy_id)
    except BookCopy.DoesNotExist:
        return render_not_found(request, item_name='Book copy')
    book_desc = get_book_details(book_copy)
    return render_response(request, 'bookcopy.html',
        {
            'book' : book_desc,
            'can_reserve' : request.user.has_perm('baseapp.add_reservation'),
            # 'can_rent' : request.user.has_perm('baseapp.add_rental'), and  # TODO
            # 'can_return' : request.user.has_perm('baseapp.change_rental'),  # TODO
        }
    )


@login_required
@permission_required('baseapp.list_users')
def show_users(request):
    context = {}
    # we only need to do something if some POST data was sent
    if request.method == 'POST':
        request_first_name   = request.POST['first_name'] if 'first_name' in request.POST else ''
        request_last_name    = request.POST['last_name'] if 'last_name' in request.POST else ''
        request_email        = request.POST['email'] if 'email' in request.POST else ''
        request_is_librarian = ('is_librarian' in request.POST)
        user_list = []

        # filter by beeing in Librarians group
        librarians_group = Group.objects.get(name='Librarians')  # TODO: this needs to read from somewhere
        if request_is_librarian:
            is_to_be_shown = lambda u: librarians_group in u.groups.all()
        else:
            is_to_be_shown = lambda u: True

        # searching for users
        if 'action' in request.POST and request.POST['action'] == 'Search':
            user_list = [ {'username'   : u.username,    # rather temporary here (need this when defining location-librarian relation).
                           'last_name'  : u.last_name,
                           'first_name' : u.first_name,
                           'email'      : u.email,
                           'url'        : "%d/" % u.id
                           }
                          for u in User.objects.filter(first_name__icontains=request_first_name)
                                               .filter(last_name__icontains=request_last_name)
                                               .filter(email__icontains=request_email)
                          if is_to_be_shown(u)
                        ]
        # we want search values back in appropriate fields
        search_data = {
            'first_name'   : request_first_name,
            'last_name'    : request_last_name,
            'email'        : request_email,
            'is_librarian' : request_is_librarian,
            }

        context = {
            'users'        : user_list,
            'search'       : search_data,
            'non_found'    : not len(user_list)  # if no users was found were pass True
            }
    return render_response(request, 'users.html', context)


@login_required
@permission_required('baseapp.list_users')
def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render_not_found(request, item_name='User')
    context = { 'first_name'    : user.first_name,
          'last_name'     : user.last_name,
          'email'         : user.email,
          'phones'        : get_phones_for_user(user),
          'building'      : user.get_profile().building,
          'rentals'       : 'rentals/',
          'reservations'  : 'reservations/',
        }
    return render_response(request, 'user.html', context)


@login_required
def edit_user_profile(request, profile_edit_form=ProfileEditForm):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return render_not_found(request, item_name='User')
    context = { 'first_name'   : user.first_name,
                'user_id'      : user.id,
                'last_name'    : user.last_name,
                'email'        : user.email,
                'building'     : user.get_profile().building,
                'phones'       : get_phones_for_user(user),
                'rentals'      : 'rentals/',
                'reservations' : 'reservations/',
                }
    if request.method == 'POST':
        form = profile_edit_form(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            context.update({'form_content' : profile_edit_form(user=user),
                            'edit_info'    : 'Edit successful',})
            return render_response(request, 'profile.html', context)
    else:
        form = profile_edit_form(user=user)

    context['form_content'] = form

    return render_response(request, 'profile.html', context)


def show_user_rentals(request, user_id):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render_not_found(request, item_name='User')
    post = request.POST
    if request.method == 'POST' and 'returned' in post:
        try:
            returned_rental = Rental.objects.get(id=post['returned'])
        except Rental.DoesNotExist:
            return render_not_found(request, item_name='Rental')
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
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return render_not_found(request, item_name='User')

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
        { 'user_id'     : user.id,
          'first_name'  : user.first_name,
          'last_name'   : user.last_name,
          'email'       : user.email,
          'rentals'     : rent_list,
        }
    )


def show_user_reservations(request, user_id):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render_not_found(request, item_name='User')
    if request.method == 'POST':
        post = request.POST
        librarian = request.user
        if 'reservation_id' in post:
            try:
                reservation = Reservation.objects.get(id=post['reservation_id'])
            except Reservation.DoesNotExist:
                return render_not_found(request, item_name='Reservation')
            rent(reservation, librarian)

    user_reservations = Reservation.objects.filter(for_whom=user).filter(rental=None).filter(when_cancelled=None)
    reservation_list = [ {'id' : r.id,
                          'url' : unicode(r.id) + u'/',
                          'book_copy_id' : r.book_copy.id,
                          'shelf_mark' : r.book_copy.shelf_mark,
                          'rental_impossible' : '' if is_reservation_rentable(r) else reservation_status(r),
                          'title' : r.book_copy.book.title,
                          'authors' : [a.name for a in r.book_copy.book.author.all()],
                          'from_date' : r.start_date,
                          'to_date' : r.end_date,
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
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return render_not_found(request, item_name='User')

    post = request.POST
    if request.method == 'POST' and 'reservation_id' in post:
        print 'Cancelling ' + post['reservation_id']
        cancel_reservation(Reservation.objects.get(id=post['reservation_id']), request.user)

    user_reservations = Reservation.objects.filter(for_whom=user).filter(Q_reservation_active)
    reservation_list = [ {'id' : r.id,
                          'url' : unicode(r.id) + u'/',
                          'book_copy_id' : r.book_copy.id,
                          'shelf_mark' : r.book_copy.shelf_mark,
                          'rental_impossible' : '' if is_reservation_rentable(r) else reservation_status(r),
                          'title' : r.book_copy.book.title,
                          'authors' : [a.name for a in r.book_copy.book.author.all()],
                          'from_date' : r.start_date,
                         } for r in user_reservations]
    return render_response(request,
        'my_reservations.html',
        { 'user_id'        : user.id,
          'first_name'     : user.first_name,
          'last_name'      : user.last_name,
          'email'          : user.email,
          'reservations'   : reservation_list,
          'cancel_all_url' : 'cancel-all/',
        }
    )


def show_reports(request):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_reports'):
        return render_forbidden(request)
    report_types = [{'name': u'Library status', 'value': u'status'},
                    {'name': u'Most often rented books', 'value': u'most_often_rented'},
                    {'name': u'Most often reserved books', 'value': u'most_often_reserved'},
                    {'name': u'Users black list', 'value': u'black_list'},
                    {'name': u'Unavailable books', 'value': u'lost_books'}]
    select_size = unicode(len(report_types))

    post = request.POST
    if request.method == 'POST':
        search_data = {'from': post['from'], 'to': post['to']}
        if 'action' in post and post['action'] == u'Export to csv':
            if ('from' in post) and ('to' in post) and ('report_type' in post):
                response = generate_csv(post['report_type'], post['from'], post['to'])
                return response

        if 'action' in post and post['action'] == u'Show':
            if ('from' in post) and ('to' in post) and ('report_type' in post):
                report_data = get_report_data(post['report_type'], post['from'], post['to'])
                report = report_data['report']
                template = report_data['template']
                error = report_data['error']
                if not error:
                    template = 'reports/' + template

                select_if_chosen = lambda d: d.update({'selected': True}) if d['value'] == post['report_type'] else d
                map(select_if_chosen, report_types)
                return render_response( request,
                                        template,
                                        {
                                            'select_size': select_size,
                                            'error': error,
                                            'search': search_data,
                                            'report_types': report_types,
                                            'report': report
                                        })

    return render_response(request, 'reports.html', {'report_types': report_types, 'select_size': select_size})


def find_book_for_user(request, user_id, book_id=None):
    if not book_id:
        return show_books(request, user_id)
    else:
        return show_book(request, book_id, user_id)


def reserve_for_user(request, user_id, book_copy_id):
    return reserve(request, book_copy_id, user_id)


def show_user_reservation(request, user_id, reservation_id):
    return render_not_implemented(request)


def reserve(request, copy, non_standard_user_id=False):  # when non_standard_user_id is set then this view allows also renting
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.add_reservation'):
        return render_forbidden(request)
    try:
        book_copy = BookCopy.objects.get(id=copy)
    except BookCopy.DoesNotExist:
        return render_not_found(request, item_name='Book copy')
    reserved = {}
    rented = {}
    post = request.POST
    try:
        if non_standard_user_id:
            nonstandard_user = User.objects.get(id=non_standard_user_id)
    except User.DoesNotExist:
        return render_not_found(request, item_name='User')
    user = request.user if non_standard_user_id == False else nonstandard_user
    if request.method == 'POST':
        r = Reservation(who_reserved=request.user, book_copy=book_copy, for_whom=user)
        if 'action' in post and post['action'].lower() == 'reserve':
            failed = False  # TODO rozwiazac to ladniej
            if 'from' in post and post['from'] != u'':
                try:
                    [y, m, d] = map(int,post['from'].split('-'))
                    r.start_date = date(y, m, d)
                except:  # TODO jaki to wyjatek
                    reserved.update({'error' : 'error - possibly incorrect date format'})
                    failed = True
            else:
                r.start_date = date.today()
            if 'to' in post and post['to'] != u'':
                try:
                    [y, m, d] = map(int,post['to'].split('-'))
                    r.end_date = date(y, m, d)
                    if (r.end_date - r.start_date).days < 0:
                        reserved.update({'error' : 'Reservation end date must be later than start date'})
                        failed = True
                    if (r.end_date - r.start_date).days > config.get_int('rental_duration'):
                        reserved.update({'error' : 'You can\'t reserve for longer than %d days' % config.get_int('rental_duration')})
                        failed = True
                except:  # TODO jaki to wyjatek
                    reserved.update({'error' : 'error - possibly incorrect date format'})
                    failed = True
            else:
                reserved.update({'error' : 'You need to specify reservation end date'})
                failed = True
            if not failed:
                r.save()
                mail.made_reservation(r)

                reserved.update({'ok' : 'ok'})
                reserved.update({'msg' : config.get_str('message_book_reserved') % (r.start_date.isoformat(), r.end_date.isoformat())})
                reserved.update({'from' : r.start_date.isoformat()})
                reserved.update({'to' : r.end_date.isoformat()})
        elif 'action' in post and post['action'].lower() == 'rent' and request.user.has_perm('baseapp.add_rental') and is_book_copy_rentable(book_copy):
                r.start_date = date.today()
                r.end_date = date.today() + timedelta(aux.book_copy_status(book_copy).rental_possible_for_days())
                try:
                    if 'to' in post and post['to'] != '':
                        [y, m, d] = map(int,post['to'].split('-'))
                        if r.end_date > date(y, m, d):
                            r.end_date = date(y, m, d)
                except:
                    print 'error in reserve - failed when renting'
                    pass  # TODO
                r.save()
                rental = Rental(reservation=r, start_date=date.today(), who_handed_out=request.user)
                rental.save()
                mail.made_rental(rental)
                rented.update({'until' : r.end_date.isoformat()})
                reserved.update({'ok' : False})

    book_desc = get_book_details(book_copy)

    for_whom = aux.user_full_name(non_standard_user_id)

    return render_response(request, 'reserve.html',
        {
            'book' : book_desc,
            'reserved' : reserved,
            'rented' : rented,
            'for_whom' : for_whom,
            'can_reserve' : request.user.has_perm('baseapp.add_reservation') and book_copy.state.is_visible,
            'can_rent' : request.user.has_perm('baseapp.add_rental') and non_standard_user_id,
            'rental_possible' : is_book_copy_rentable(book_copy)
        }
    )


def cancel_all_my_reserevations(request):
    return cancel_all_user_resevations(request, request.user.id)


def cancel_all_user_resevations(request, user_id):
    user = User.objects.get(id=user_id)
    canceller = request.user
    post = request.POST

    if request.method == 'POST' and 'sure' in post and post['sure'] == 'true':
        aux.cancel_all_user_resevations(canceller, user)

        return render_response(request, 'reservations_cancelled.html',
            { 'first_name' : user.first_name,
              'last_name'  : user.last_name,
              'email'      : user.email,
            })

    else:
        return render_response(request, 'cancel_reservations.html',
            { 'first_name' : user.first_name,
              'last_name'  : user.last_name,
              'email'      : user.email,
            })
