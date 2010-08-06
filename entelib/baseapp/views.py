# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from baseapp.config import Config
from baseapp.exceptions import EntelibWarning
from baseapp.forms import RegistrationForm, ProfileEditForm, BookRequestForm, ConfigOptionEditForm
from baseapp.models import *
from baseapp.reports import get_report_data, generate_csv
from baseapp.utils import pprint, str_to_date, remove_non_ints
from baseapp.time_bar import get_time_bar_code_for_copy, TimeBarRequestProcessor
from baseapp.views_aux import render_forbidden, render_response,     filter_query, get_phones_for_user, reservation_status, is_reservation_rentable, rent, mark_available, render_not_implemented, render_not_found, is_book_copy_rentable, get_locations_for_book, Q_reservation_active, cancel_reservation, when_copy_reserved
import baseapp.views_aux as aux
import baseapp.emails as mail
import settings

today = date.today

@permission_required('baseapp.load_default_config')
def load_default_config(request, do_it=False):
    '''
    Restores default values to config. This is rather for developement than production usage.
    '''
    if do_it:
        from dbconfigfiller import fill_config
        fill_config()
    return render_response(request, 'load_default_config.html', {})


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
            value = request.POST['value']
            msg = 'Key %s has now value %s' % (option_key, value)
            messages.success(request, msg)
            return HttpResponseRedirect('/entelib/config/')
    # display fresh new form
    else:
        form = edit_form(user=user, option_key=option_key, initial=form_initial)

    form.option_key = option_key
    form.description = config.get_description(option_key)
    form.can_override = config.can_override(option_key)
    context['form'] = form
    return render_response(request, tpl_edit_option, context)


@permission_required('baseapp.list_emaillog')
def show_email_log(request):
    '''
    Handles listing all sent emails (logged messages, not adresses).
    '''
    template = 'email/list.html'
    context = {
        'emails' : EmailLog.objects.all().order_by('-sent_date'),
        }

    return render_response(request, template, context)


@permission_required('baseapp.add_bookrequest')
def request_book(request, request_form=BookRequestForm):
    '''
    Handles requesting for book by any user.
    '''
    user = request.user

    template = 'book_request.html'
    context = {}

    # redisplay form
    if request.method == 'POST':
        form = request_form(user=user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            context['show_confirmation_msg'] = True
            return render_response(request, template, context)
    # display fresh new form
    else:
        form = request_form(user=user)

    context['form_content'] = form
    context['books'] = Book.objects.all()
    context['requested_items'] = BookRequest.objects.all()
    return render_response(request, template, context)


@transaction.commit_on_success
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
        if action == 'newactiveuser':
            # commit
            if request.method == 'POST':
                form = registration_form(data=request.POST, files=request.FILES)
                if form.is_valid():
                    new_user = form.save()
                    new_user.is_active = True
                    new_user.save()
                    messages.success(request, 'User registered and activated.')
                    return HttpResponseRedirect('/entelib/users/%d/' % new_user.id)
            # display form
            else:
                form = registration_form()

            # prepare response
            result_context = { 'form_content' : form }
            result_context.update(extra_context)
            return render_response(request, tpl_registration_form, result_context)
        else:
            return render_response(request, tpl_logout_first)
    else:   # not authenticated
        if action == 'newuser':
            # commit new user
            if request.method == 'POST':
                form = registration_form(data=request.POST, files=request.FILES)
                if form.is_valid():
                    new_user = form.save()
                    messages.success(request, 'User registered, wait for activation.')
                    return HttpResponseRedirect('/entelib/')
            # display form
            else:
                form = registration_form()

            # prepare response
            result_context = { 'form_content' : form }
            result_context.update(extra_context)
            return render_response(request, tpl_registration_form, result_context)
        else:  # action other than newuser
            return render_not_found(request, item='Action')


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/entelib/')


@login_required
def default(request):
    return render_response(request, 'entelib.html')


@login_required
def my_new_reservation(request): # that is kinda hack, but I couldn't think of any better way of doing that
    return HttpResponseRedirect('/entelib/books/')


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
        book_url = u'/entelib/users/%d/reservations/new/book/%s/' % (int(non_standard_user_id), '%d')
    bookcopy_url = u'/entelib/bookcopy/%d/'    # where you go after clicking "search" button with shelf mark field (ID) filled
    if non_standard_user_id is not False:  # and where you go if there is a non std user given and you filled shelf mark (ID) field
        bookcopy_url = u'/entelib/users/%d/reservations/new/bookcopy/%s/' % (int(non_standard_user_id), '%d')
    config = Config(request.user)
    search_data = {}                    # data of searching context
    selected_categories_ids = []        # ids of selected categories -- needed to reselect them on site reload
    bookcopies = None                   # if one doesn't type into shelf mark field we are not interested in bookcopies at all
    books = []
    shelf_mark = None

    # if POST is sent we need to take care of some things
    if request.method == 'POST':
        post = request.POST
        # case 1: searching by shelf mark. Other fields are ignored
        if 'id' in post and post['id'] != '':
            shelf_mark = post['id']
            search_data.update({'id' : shelf_mark})
            booklist = BookCopy.objects.filter(shelf_mark__startswith=shelf_mark)
            bookcopies = [{'shelf_mark' : b.shelf_mark, 
                           'state'      : aux.book_copy_status(b),
                           'title'      : b.book.title, 
                           'authors'    : [a.name for a in b.book.author.all()],
                           'location'   : b.location.building.name + ' - ' + b.location.details,
                           'url'        : bookcopy_url % b.id,
                           }       for b in booklist]

        else:
            search_title = post['title'].split()
            search_author = post['author'].split()
            selected_categories_ids = map(int, request.POST.getlist('category'))
            search_data.update({'title'  : post['title'], 
                                'author' : post['author'],
                                })  # categories and checkboxes will be added later

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
            search_data.update({ 'title_any_checked'      : 'true' if 'title_any' in post else '',
                                 'author_any_checked'     : 'true' if 'author_any' in post else '',
                                 'category_any_checked'   : 'true' if 'category_any' in post else '',
                                 })

            # prepare each book (add url, list of authors) for rendering
            books = [{ 'title'     : book.title,
                       'url'       : book_url % book.id,
                       'authors'   : [a.name for a in book.author.all()]
                       } for book in booklist ]
    else:
        # If no POST data was sent, then we don't want to list any books, but we want
        # to fill category selection input with all possible categories.
        if config.get_bool('list_only_existing_categories_in_search'):
            categories_from_booklist = list(set([c for b in Book.objects.all() for c in b.category.all()]))
        else:
            categories_from_booklist = Category.objects.all()

    # prepare categories for rendering
    search_categories  = [ {'name' : '-- Any --',  'id' : 0} ]
    if bookcopies is None:
        # we only render categories if we are not searching by shelf mark
        search_categories += [ {'name' : c.name,  'id' : c.id,  'selected': c.id in selected_categories_ids }  for c in categories_from_booklist ]

    # update search context
    search_data.update({'categories' : search_categories,
                        'categories_select_size' : min(len(search_categories), config.get_int('categories_select_size')),
                        })

    for_whom = aux.user_full_name(non_standard_user_id)

    context = {
        'for_whom' : for_whom,
        'books' : books,
        'bookcopies' : bookcopies,
        'search' : search_data,
        'can_add_book' : request.user.has_perm('baseapp.add_book'),
        'none_found' : not len(books) and request.method == 'POST'
        }
    return render_response(request, 'books.html', context)


@login_required
def show_book(request, book_id, non_standard_user_id=False):
    '''
    Finds all copies of a book.
    '''
    config = Config(request.user)
    context = {}
    
    # if we have a non_standard_user we treat him special
    url_for_non_standard_users = u'/entelib/users/%d/reservations/new/bookcopy/%s/' % (int(non_standard_user_id), u'%d')
    show_url = u'/entelib/bookcopy/%d/' if non_standard_user_id == False else url_for_non_standard_users
    if non_standard_user_id == False:
        if request.user.has_perm('baseapp.add_rental'):
            reserve_url = u'/entelib/bookcopy/%d/user/'
        else:
            reserve_url = u'/entelib/bookcopy/%d/reserve/'
    else:
        reserve_url = url_for_non_standard_users
    # do we have such book?
    book = get_object_or_404(Book,id=book_id)
    ## try:
    ##     book = Book.objects.get(id=book_id)
    ## except Book.DoesNotExist:
    ##     return render_not_found(request, item_name='Book')
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
                book_copies = book_copies.filter(state__is_available=True)
    curr_copies = []
    
    # time bar generating
    tb_processor = TimeBarRequestProcessor(request, None, config)  # default date range
    tb_context = tb_processor.get_context()
    tb_copies = tb_processor.get_codes_for_copies(book_copies)
    context.update(tb_context)
    
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
            'tb_code'       : tb_copies.get(elem.id),
            })
    # dict for book
    book_desc = {
        'id'          : book.id,
        'title'       : book.title,
        'authors'     : [a.name for a in book.author.all()],
        'items'       : curr_copies,
        'categories'  : [c.name for c in book.category.all()],
        }
    locations_for_book = get_locations_for_book(book.id)
    search_locations = []
    if locations_for_book: 
        search_locations += [{'name' : '-- Any --', 'id' : 0, 'selected': len(selected_locations)==0}]
        search_locations += [{'name' : unicode(loc),
                              'id' : loc.id,
                              'selected': loc.id in selected_locations}
                              for loc in locations_for_book]
    search_data = {
        'locations' : search_locations,
        'copies_location_select_size': min(len(search_locations), config.get_int('copies_location_select_size')),      # count of elements displayed in <select> tag
        }

    for_whom = aux.user_full_name(non_standard_user_id)
    last_date = date.today() + timedelta(config.get_int('when_reserved_period'))

    context.update({ 'book'                   : book_desc,
                     'last_date'              : last_date,
                     'search'                 : search_data,
                     'for_whom'               : for_whom,
                     'can_add_bookcopy'       : request.user.has_perm('baseapp.add_bookcopy'),
                     'only_available_checked' : 'yes' if 'available' in request.POST else '',
                     })
    return render_response(request, 'bookcopies.html', context)


@login_required
def show_book_copy(request, bookcopy_id):
    '''
    Shows book copy's details
    '''
    config = Config(request.user)
    book_copy = get_object_or_404(BookCopy, id=bookcopy_id)
    book_desc = aux.get_book_details(book_copy)
    
    context = {
        'book' : book_desc,
    }
    
    tb_processor = TimeBarRequestProcessor(request, None, config)  # default date range
    tb_context = tb_processor.get_context(book_copy)
    context.update(tb_context)
    
    return render_response(request, 'bookcopy.html', context)


@login_required
def book_copy_up_link(request, bookcopy_id):
    book_id = get_object_or_404(BookCopy, id=bookcopy_id).book.id
    return HttpResponseRedirect('/entelib/books/%s/' % book_id)


def user_book_copy_up_link(request, user_id, bookcopy_id):
    book_id = get_object_or_404(BookCopy, id=bookcopy_id).book.id
    return HttpResponseRedirect('/entelib/users/%s/reservations/new/books/%s/' % (user_id,  book_id))


@permission_required('baseapp.list_users')
def find_user_to_rent_him(request):
    show_users(request) 


@permission_required('baseapp.list_users')
def show_users(request):
    template = 'users.html'
    context = {}
    buildings = [{'id':0, 'name':'Any'}] + list(Building.objects.values('id', 'name'))
    context.update({'buildings' : buildings})

    if request.method == 'POST':
        post = request.POST
        request_first_name       = post['first_name'].strip() if 'first_name' in post else ''
        request_last_name        = post['last_name'].strip() if 'last_name' in post else ''
        request_email            = post['email'].strip() if 'email' in post else ''
        request_from_my_building = 'from_my_building' in post
        request_building_id      = int(post['building'])
        user_list = []

        # searching for users
        if 'action' in post and post['action'] == 'Search':
            if request_from_my_building:
                request_building_id = request.user.userprofile.building.id

            user_list = aux.get_users_details_list(request_first_name, request_last_name, request_email, request_building_id)

        # we want search values back in appropriate fields
        search_data = {
            'first_name'       : request_first_name,
            'last_name'        : request_last_name,
            'email'            : request_email,
            }

        try:
            building_pair = {'id' : request_building_id, 'name' : Building.objects.get(id=request_building_id).name}
            building_index = buildings.index(building_pair)
        except Building.DoesNotExist: # ValueError:
            building_index = 0
            
        context['buildings'][building_index].update({'selected' : True})

        context.update({
            'users'            : user_list,
            'search'           : search_data,
            'non_found'        : not len(user_list),  # if no users was found were pass True
            'from_my_building' : request_from_my_building,
            })
    return render_response(request, template, context)


@permission_required('auth.add_user')
def add_user(request, registration_form=RegistrationForm):
    return register(request, 'newactiveuser')


@permission_required('baseapp.list_users')
def show_user(request, user_id, redirect_on_success_url='/entelib/users/%d/', profile_edit_form=ProfileEditForm):
    user_id = int(user_id)
    edited_user = get_object_or_404(User, id=user_id)
    return _do_edit_user_profile(request, edited_user, redirect_on_success_url, profile_edit_form)


def _do_edit_user_profile(request, edited_user, redirect_on_success_url='/entelib/users/%d/', profile_edit_form=ProfileEditForm):
    ''' 
    Displays form for editing user's profile.
    
    request.user -- user editing someone's profile (it can be his own profile)
    edited_user -- user, whose profile will be edited.
    '''
    if '%d' in redirect_on_success_url:
        redirect_on_success_url = redirect_on_success_url % edited_user.id
    
    form_initial = profile_edit_form.get_initials_for_user(edited_user)
    can_change_profile = request.user.id == edited_user.id or request.user.has_perm('auth.change_user')
    if request.method == 'POST' and can_change_profile:
        # use data from post to fill form
        form = profile_edit_form(edited_user, editor=request.user, data=request.POST, initial=form_initial)
        if form.is_valid():
            # notify data changed and display profile
            form.save()
            messages.success(request, 'Profile details updated.')
            return HttpResponseRedirect(redirect_on_success_url)
    else:
        # no POST implies fresh form with profiles' data
        form = profile_edit_form(edited_user, editor=request.user, initial=form_initial)

    # prepare context and render site
    context = profile_edit_form.build_default_context_for_user(edited_user)
    context['form_content'] = form
    return render_response(request, 'profile.html', context)


@login_required
def edit_user_profile(request, redirect_on_success_url=u'/entelib/profile/', profile_edit_form=ProfileEditForm):
    ''' 
    Displays form for editing user's profile, where user means request.user
    '''
    # well, this is the same that user A edits profile of user B, where A==B
    return _do_edit_user_profile(request, request.user, redirect_on_success_url, profile_edit_form)


@permission_required('baseapp.list_users')
def show_user_rentals(request, user_id):
    return aux.show_user_rentals(request, user_id)


@login_required
def show_my_rentals(request):
    return aux.show_user_rentals(request)


@permission_required('baseapp.list_users')
def show_user_reservations(request, user_id):
    return aux.show_user_reservations(request, user_id)


@permission_required('baseapp.list_users')
def show_user_reservation_archive(request, user_id):
    return aux.show_user_reservation_archive(request, user_id)


@login_required
def show_my_reservation_archive(request):
    return aux.show_user_reservation_archive(request)
 

@permission_required('baseapp.list_users')
def show_user_rental_archive(request, user_id):
    return aux.show_user_rental_archive(request, user_id)


@login_required
def show_my_rental_archive(request):
   return aux.show_user_rental_archive(request)


@login_required
def show_my_reservations(request):
    return aux.show_user_reservations(request)


@permission_required('baseapp.list_reports')
def show_reports(request, name=''):
    template_for_report = {'status'              : 'reports/library_status.html',
                           'black_list'          : 'reports/black_list.html',
                           'lost_books'          : 'reports/unavailable_status.html',
                           'most_often_rented'   : 'reports/most_often_rented.html',
                           'most_often_reserved' : 'reports/most_often_reserved.html',
    }

    report_name = name
    if report_name and (report_name not in template_for_report.keys()):  # unknown report type
        raise Http404

    context = {}
    if report_name:
        post = request.POST
        from_date = date(2000, 1, 1)
        to_date = date(2500, 1, 1)
        if 'from' in post:
            from_date = str_to_date(post['from'], from_date)
        if 'to' in post:
            to_date = str_to_date(post['to'], to_date)
        search_data = {'from': unicode(from_date), 'to': unicode(to_date)}
        context['search'] = search_data
        
        if request.method == 'POST':
            if 'btn_show' in post:
                order_by = []
                if 'ordering' in post:
                    order_by.append(post['ordering'])
                report_data = get_report_data(report_name, unicode(from_date), unicode(to_date), order_by=order_by)
                context['error'] = report_data['error']
                context['report'] = report_data['report']
                context['ordering'] = report_data['ordering']
                return render_response(request, template_for_report[report_name], context)
            elif 'btn_generate_csv' in post:
                order_by = []
                if 'ordering' in post:
                    order_by.append(post['ordering'])
                response = generate_csv(report_name, unicode(from_date), unicode(to_date), order_by=order_by)
                return response
            else:  # sort command lookup
                btn_sort_prefix = 'btn_sort_'
                order_by = [ k[len(btn_sort_prefix):] for k in post.keys() if k.startswith(btn_sort_prefix)]
                if not order_by:
                    return render_not_found(request, msg='Action not recognized')
                
                report_data = get_report_data(report_name, unicode(from_date), unicode(to_date), order_by=order_by)
                context['error'] = report_data['error']
                context['report'] = report_data['report']
                context['ordering'] = report_data['ordering']
                return render_response(request, template_for_report[report_name], context)
                
        else:
            order_by = []
            if 'ordering' in post:
                order_by.append(post['ordering'])
            report_data = get_report_data(report_name, unicode(from_date), unicode(to_date), order_by=order_by)
            context['report'] = report_data['report']
            context['error']  = report_data['error']
            context['ordering'] = report_data['ordering']
            return render_response(request, template_for_report[report_name], context)
    else:       
        return render_response(request, 'reports.html', context)


@permission_required('baseapp.list_users')
def find_book_for_user(request, user_id, book_id=None):
    if not book_id:
        return show_books(request, user_id)
    else:
        return show_book(request, book_id, user_id)


@permission_required('baseapp.list_users')
def reserve_for_user(request, user_id, book_copy_id):
    return reserve(request, book_copy_id, user_id)


@login_required
def show_user_reservation(request, user_id, reservation_id):
    return render_not_implemented(request)


@permission_required('baseapp.add_reservation')
def reserve(request, copy, non_standard_user_id=False):  # when non_standard_user_id is set then this view allows also renting
    book_copy = get_object_or_404(BookCopy, id=copy)
    config = Config(user=request.user)
    reserved = {}   # info on reservation
    context = {'reserve_from' : today(),
               'reserve_to'   : today() + timedelta(Config(user=request.user).get_int('reservation_duration')),
               }
#    rented = {}     # info on rental
    if non_standard_user_id:
        non_standard_user = get_object_or_404(User,id=non_standard_user_id)
    user = request.user if not non_standard_user_id else non_standard_user
    # all the work needs to be done if there is some (POST) data sent:
    post = request.POST
    if request.method == 'POST':
        # if clicked rent/reserve, not time bar button:
        if 'action' in post and post['action'] in ['reserve', 'rent']:
            context.update({'reserve_from' : post['from'], 'reserve_to' : post['to']})

        # we need reservation, whether we rent or just reserve:
        r = Reservation(who_reserved=request.user, book_copy=book_copy, for_whom=user)

        # reserve requested:
        if 'action' in post and post['action'].lower() == 'reserve':
            try:
                if 'from' in post and post['from'] != u'':
                    try:
                        [y, m, d] = map(int,post['from'].split('-'))
                        r.start_date = date(y, m, d)
                    except ValueError:
                        raise EntelibWarning('Error - probably incorrect date format.')
                else:
                    raise EntelibWarning('You need to specify reservation start date')
                if 'to' in post and post['to'] != u'':
                    try:
                        [y, m, d] = map(int,post['to'].split('-'))
                        r.end_date = date(y, m, d)
                        if r.start_date < today():
                            raise EntelibWarning('Reservation cannot begin in the past.')
                        if r.end_date < r.start_date:
                            raise EntelibWarning('"From" date cannot be later than "To" date.')
                        if (r.end_date - r.start_date).days > config.get_int('reservation_duration'):
                            raise EntelibWarning('You can\'t reserve for longer than %d days' % config.get_int('reservation_duration'))
                    except ValueError:
                        raise EntelibWarning('error - possibly incorrect date format')
                elif r.start_date:
                    raise EntelibWarning('You need to specify reservation end date')
            except EntelibWarning, e:
                reserved.update({'error' : str(e)})
            else:
                r.save()
                mail.made_reservation(r)

                reserved.update({'ok' : 'ok'})
                reserved.update({'msg' : config.get_str('message_book_reserved') % (r.start_date.isoformat(), r.end_date.isoformat())})
                reserved.update({'from' : r.start_date.isoformat()})
                reserved.update({'to' : r.end_date.isoformat()})
        # renting action requested
        elif 'action' in post and post['action'].lower() == 'rent':
            if not request.user.has_perm('baseapp.add_rental'):
                raise PermissionDenied('User not allowed to rent')
            if not is_book_copy_rentable(book_copy):
                return aux.render_forbidden(request, 'Book copy not rentable')
            r.start_date = date.today()  # always rent from now
            # for how long rental is possible
            max_end_date = date.today() + timedelta(aux.book_copy_status(book_copy).rental_possible_for_days())
            try:
                if 'to' in post and post['to'] != '':
                    [y, m, d] = map(int,post['to'].split('-'))
                    desired_end_date = date(y, m, d)
                    # if user wants book for shorter than max allowed period
                    if desired_end_date <= max_end_date :
                        r.end_date = desired_end_date
                    else:
                        raise EntelibWarning("Rental must end before %s." % max_end_date.isoformat())
                    if r.end_date < today():
                        raise EntelibWarning("Reservation can't end before today.")
                else:
                    raise EntelibWarning('You need to specify reservation end date')
                r.save()

                # reservation done, rent:
                rental = Rental(reservation=r, start_date=date.today(), who_handed_out=request.user)
                rental.save()
                mail.made_rental(rental)  # notifications
                reserved.update({'msg' : config.get_str('message_book_rented') % r.end_date.isoformat()})
            except ValueError:
                reserved.update({'error' : 'error - possibly incorrect date format'})
            except EntelibWarning, w:
                reserved.update({'error' : str(w)})
            
    book_desc = aux.get_book_details(book_copy)

    for_whom = aux.user_full_name(non_standard_user_id)
    # if for_whom:
    #     context.update({'user' : User.objects.get(id=non_standard_user_id)})

    # TODO: default start/end dates
    context.update({
        'book'            : book_desc,
        'reserved'        : reserved,
        'for_whom'        : for_whom,
        'can_reserve'     : request.user.has_perm('baseapp.add_reservation') and book_copy.state.is_visible,
        'rental_possible' : is_book_copy_rentable(book_copy),
    })

    # time bar        
    tb_processor = TimeBarRequestProcessor(request, None, config)  # default date range
    tb_context = tb_processor.get_context(book_copy)
    context.update(tb_context)

    return render_response(request, 'reserve.html', context)


@permission_required('baseapp.change_own_reservation')
def cancel_all_my_reserevations(request):
    aux.cancel_user_resevations(user=request.user, canceller=request.user)
    return render_response(request, 'reservations_cancelled.html', {})

@permission_required('baseapp.list_users')
@permission_required('baseapp.change_reservation')
def cancel_all_user_resevations(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        render_not_found(request, item='User')
    canceller = request.user
    post = request.POST

    if request.method == 'POST' and 'sure' in post and post['sure'] == 'true':
        aux.cancel_user_resevations(canceller, user)

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


@permission_required('baseapp.list_locations')
def show_locations(request):
    locs = Location.objects.select_related().all()
    context = {'rows' : locs,
               }
    return render_response(request, 'locations/list.html', context)


@permission_required('baseapp.view_location')
def show_location(request, loc_id):
    try:
        loc_id = int(loc_id)
    except ValueError:
        loc_id = -1   # will cause 404

    location = get_object_or_404(Location, pk=loc_id)
    context = {
        'loc'         : location,
        'maintainers' : location.maintainer.all(),
        }
    return render_response(request, 'locations/one.html', context)
