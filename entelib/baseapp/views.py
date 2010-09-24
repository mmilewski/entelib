# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from baseapp.config import Config
from baseapp.exceptions import EntelibWarning
import baseapp.forms as forms
from baseapp.models import *
from baseapp.reports import get_report_data, generate_csv
from baseapp.utils import pprint
import baseapp.utils as utils
from baseapp.time_bar import get_time_bar_code_for_copy, TimeBarRequestProcessor
from baseapp.views_aux import render_forbidden, render_response, get_phones_for_user, reservation_status, is_reservation_rentable, rent, mark_available, render_not_implemented, render_not_found, get_locations_for_book, Q_reservation_active, cancel_reservation, filter_query
import baseapp.views_aux as aux
import baseapp.emails as mail
import settings
from itertools import chain


today = date.today
now = datetime.datetime.now  # this seems like an error, but it stopped working as "now = datetime.now"

@permission_required('baseapp.load_default_config')
def load_default_config(request, do_it=False):
    """
    Restores default values to config. This is rather for developement than production usage.
    """
    context = {}
    if do_it:
        from dbconfigfiller import fill_config
        fill_config()
        context['confirmation'] = 'Default configuration loaded'
        messages.info(request, 'Default config loaded.')
    return render_response(request, 'load_default_config.html', context)


@permission_required('baseapp.list_config_options')
def show_config_options_per_user(request):
    """
    Handles listing config options from Configuration model (also Config class).
    """
    template = 'config/list.html'
    config = Config(user=request.user)
    opts = config.get_all_options().values()
    lex_by_key = lambda a,b : -1 if a.key < b.key else (1 if a.key > b.key else 0)
    opts.sort(cmp=lex_by_key)
    can_edit_global = False
    context = {
        'can_edit_global_config' : can_edit_global,
        'options'                : opts,
        }
    return render_response(request, template, context)


@permission_required('baseapp.list_config_options')
def show_config_options(request):
    """
    Handles listing config options from Configuration model (also Config class).
    """
    template = 'config/list.html'
    config = Config(user=request.user)
    opts = config.get_all_options().values()
    lex_by_key = lambda a,b : -1 if a.key < b.key else (1 if a.key > b.key else 0)
    opts.sort(cmp=lex_by_key)
    can_edit_global = aux.can_edit_global_config(request.user)
    context = {
        'can_edit_global_config' : can_edit_global,
        'options'                : opts,
        }
    return render_response(request, template, context)


@permission_required('baseapp.edit_option')
def edit_config_option(request, option_key, is_global=False, edit_form=forms.ConfigOptionEditForm):
    """
    Handles editing config option by user.
    """
    isinstance(is_global, bool)
    tpl_edit_option = 'config/edit_option.html'
    user = request.user
    if is_global:
        config = Config()
    else:
        config = Config(user)

    redirect_response_here = HttpResponseRedirect(settings.LOGIN_URL + '?next=' + request.get_full_path())
    if is_global and (not aux.can_edit_global_config(user)):  # edit global without perms
        return redirect_response_here
    if (not is_global) and (not config.can_override(option_key)):         # edit local unoverridable key
        return redirect_response_here

    if option_key not in config:
        return render_not_found(request, item_name='Config option')

    option = { 'can_override'  : config.can_override(option_key),
               'description'   : config.get_description(option_key),
        } 
    context = {
        'is_global'   : is_global,
        'option'      : option,
        }
    form_initial = {'value'         : config[option_key],
                    'can_override'  : option['can_override'],
                    'description'   : option['description'], 
        }
    # redisplay form
    if request.method == 'POST':
        form = edit_form(user=user, option_key=option_key, config=config, is_global=is_global, data=request.POST, initial=form_initial)
        if form.is_valid():
            form.save()
#            value = request.POST['value']
#            print value
            msg = 'Key %s has now value: %s' % (option_key, config[option_key])
            messages.success(request, msg)
            if is_global: 
                return HttpResponseRedirect(reverse('config_all'))
            else:
                return HttpResponseRedirect(reverse('profile_config'))
        else:
            pass
    # display fresh new form
    else:
        form = edit_form(user=user, option_key=option_key, config=config, is_global=is_global, initial=form_initial)

    form.option_key = option_key
    form.description = config.get_description(option_key)
    form.can_override = config.can_override(option_key)
    context['form'] = form
    return render_response(request, tpl_edit_option, context)


@permission_required('baseapp.list_emaillog')
def show_email_log(request):
    """
    Handles listing all sent emails (logged messages, not adresses).
    """
    template = 'email/list.html'
    context = {
        'emails' : EmailLog.objects.all().order_by('-sent_date'),
        }

    return render_response(request, template, context)


def show_forgot_password(request):
    from django.core.validators import email_re
    logger = utils.get_logger('view.forgot_password')
    context = {}
    context['errors'] = []
    if request.method == 'POST':
        post = request.POST
        # any email given?
        if 'email' in post and len(post['email']) > 0:
            email = post['email']
            context['email'] = email
            # invalid ~~> show error?
            if not email_re.match(post['email']):
                context['errors'].append('Enter a valid e-mail address.')
            else:
                # valid email, but whether user with such exist?
                users = list(User.objects.filter(email__iexact=email))
                if len(users) > 1:
                    logger.error('%s users have email %s' % (len(users), email))
                if not users:
                    context['errors'].append("Your e-mail wasn't found in database")
                else:
                    user = users[0]
                    handler = aux.ForgotPasswordHandler(user)
                    handler.reset_password(user)
                    new_password = handler.new_password
                    messages.info(request, 'New password was sent to this email')
        else:
            context['errors'].append('This field is required.')
    else:
        pass

    return render_response(request, 'registration/forgot_password.html', context)


@transaction.commit_on_success
def register(request, action, registration_form=forms.RegistrationForm, extra_context={}):
    """
    Handles registration (adding new user) process.
    """
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
            if not request.user.has_perms(['auth.change_user', 'auth.add_user']):
                return render_forbidden(request)
            if request.method == 'POST':
                form = registration_form(data=request.POST, files=request.FILES)
                if form.is_valid():
                    new_user = form.save()
                    new_user.save()
                    new_user.is_active = True
                    new_user.save()
                    profile = new_user.userprofile
                    profile.awaits_activation = False
                    profile.save()
                    messages.success(request, 'User registered and activated.')
                    return HttpResponseRedirect('/entelib/users/%d/' % new_user.id)
            # display form
            else:
                form = registration_form()

            # prepare response
            result_context = {
                'form_content' : form,
                'is_adding_active_user' : True,
                }
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
                    messages.success(request, 'Registered as %s, wait for activation.' % new_user.username)
                    mail.user_registered(new_user)
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
    """
    Desc:
        Allows to find, and lists searched books.

    Args:
        non_standard_user_id is used when librarian is searching for a book in the name of user.
        In that case non_standard_user_id is most likely different than request.user
    """
    # data for the template
    # book_url = u'%d/'    # where you go after clicking "search" button
    # bookcopy_url = u'../bookcopy/%d/'    # where you go after clicking "search" button with shelf mark field (ID) filled
    config = Config(request.user)
    show_availability = config.get_bool('show_nr_of_available_copies')
    search_data = {}                    # data of searching context
    selected_categories_ids = []        # ids of selected categories -- needed to reselect them on site reload
    selected_location_ids = []
    selected_cc_ids = []
    bookcopies = []                     # if one doesn't type into shelf mark field we are not interested in bookcopies at all
    books = []
    shelf_mark = None
    booklist = []
    show_books = False
    
    # if POST is sent we need to take care of some things
    if request.method == 'POST':
        post = request.POST
        selected_location_ids = map(int, post.getlist('location'))
        selected_cc_ids = map(int, post.getlist('cost_center'))
        selected_categories_ids = map(int, post.getlist('category'))
        # case 1: searching by shelf mark. Other fields are ignored
        if 'id' in post and post['id'] != '':
            shelf_mark = post['id']
            search_data.update({'id' : shelf_mark})
            bookcopies = BookCopy.objects.select_related('book').filter(shelf_mark__icontains=shelf_mark).select_related('author', 'category').order_by('book__title')
        # case 2: searching by anything but shelf mark
        else:
            show_books = True
            search_title = post['title'].split()
            search_author = post['author'].split()
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
            # filter with location
            if selected_location_ids:
                bookcopies = BookCopy.objects.select_related('book', 'location').filter(location__id__in=selected_location_ids, book__in=booklist)
            # filter with cost center
            if selected_cc_ids:
                bookcopies = BookCopy.objects.select_related('book', 'location').filter(cost_center__id__in=selected_cc_ids, book__in=booklist)
            if selected_location_ids or selected_cc_ids:
                booklist = []

            # TODO: delete following commented code, remove config options for that
            # if config.get_bool('cut_categories_list_to_found_books'):
            #     # compute set of categories present in booklist (= exists book which has such a category)
            #     categories_from_booklist = list(set([c for b in booklist for c in b.category.all()]))
            # else:
            #     # list all nonempty categories
            #     categories_from_booklist = list(set([c for b in Book.objects.only('category').all() for c in b.category.all()]))

            # put ticks on previously ticked checkboxes
            search_data.update({ 'title_any_checked'      : 'true' if 'title_any' in post else '',
                                 'author_any_checked'     : 'true' if 'author_any' in post else '',
                                 'category_any_checked'   : 'true' if 'category_any' in post else '',
                                 })

    else:
        show_books = True
        if config.get_bool('list_all_books_as_default'):
            booklist = Book.objects.select_related()
    # prepare each book (add url, list of authors) for rendering
    if booklist and show_books:
        booklist = booklist.order_by('title')
        books = [{ 'book'      : book,
                   } for book in booklist ]
        if show_availability:
            for book in books:
                book.update({'nr_of_available_copies' : aux.nr_of_available_copies(book['book'])})
        
    bookcopies = [{'id'         : b.id,
                   'shelf_mark' : b.shelf_mark, 
                   'state'      : aux.book_copy_status(b),
                   'title'      : b.book.title, 
                   'authors'    : [a.name for a in b.book.author.all()],
                   'location'   : b.location,
                   # 'url'        : bookcopy_url % b.id,
                   'book'       : b.book,
                   }       for b in bookcopies ]

    # prepare categories for rendering
    search_categories  = [ {'name' : '-- Any category --',  'id' : 0} ]
    # if bookcopies is None:
    #     # we only render categories if we are not searching by shelf mark
    #     # search_categories += [ {'name' : c.name,  'id' : c.id,  'selected': c.id in selected_categories_ids }  for c in categories_from_booklist ]
    search_categories += [ {'name' : c.name,  'id' : c.id,  'selected': c.id in selected_categories_ids }  for c in Category.objects.all() ]

    search_locations = [ {'id' : l.id, 'name' : l, 'selected': l.id in selected_location_ids }  for l in Location.objects.all() ]

    search_cc = [ {'name' : c.name,  'id' : c.id,  'selected': c.id in selected_cc_ids }  for c in CostCenter.objects.all() ]
    # update search context
    search_data.update({'categories' : search_categories,
                        'locations'  : search_locations,
                        'ccs'        : search_cc,
                        'categories_select_size' : min(len(search_categories), config.get_int('categories_select_size')),
                        'copies_location_select_size' : min(len(search_locations), config.get_int('copies_location_select_size')),
                        })

    for_whom = aux.user_full_name(non_standard_user_id)
    context = {
        'for_whom' : for_whom,
        'books' : books,
        'show_availability' : show_availability,
        'bookcopies' : bookcopies,
        'search' : search_data,
        'can_add_book' : request.user.has_perm('baseapp.add_book'),
        'none_found' : not len(books) and not bookcopies and request.method == 'POST'
        }
    return render_response(request, 'books.html', context)


@login_required
def show_book(request, book_id, non_standard_user_id=False):
    """
    Finds all copies of a book.
    """
    config = Config(request.user)
    book = get_object_or_404(Book,id=book_id)
    context = {}
    
    # if we have a non_standard_user we treat him special
    # url_for_non_standard_users = u'/entelib/users/%d/bookcopy/%s/' % (int(non_standard_user_id), u'%d')
    # show_url = u'/entelib/bookcopy/%d/' if non_standard_user_id == False else url_for_non_standard_users
    # if non_standard_user_id == False:
    #     if request.user.has_perm('baseapp.add_rental'):
    #         reserve_url = u'/entelib/bookcopy/%d/user/'
    #     else:
    #         reserve_url = u'/entelib/bookcopy/%d/reserve/'
    # else:
    #     reserve_url = url_for_non_standard_users
    # do we have such book?
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
            'id'            : elem.id,
            # 'url'           : show_url % elem.id,
            # 'reserve_url'   : reserve_url % elem.id,
            'shelf_mark'    : elem.shelf_mark,
            'location'      : elem.location,
            'maintainers'   : ",".join([ "%s %s"%(f,l) for f,l in elem.location.maintainer.values_list('first_name', 'last_name') ]),
            'state'         : elem.state,
            'publisher'     : elem.publisher,
            'year'          : elem.year,
            'is_available'  : elem.state.is_available,
            'is_reservable' : is_copy_reservable,    # it allows reserving in template - true if user is allowed to reserve
            # 'when_reserved' : when_copy_reserved(elem), TODO: delete this line
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
        search_locations += [{'name' : '-- Any --',
                              'id' : 0,
                              'selected': len(selected_locations)==0 or (len(selected_locations)==1 and selected_locations[0]==0) }]
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
    """
    Shows book copy's details
    """
    config = Config(request.user)
    book_copy = get_object_or_404(BookCopy, id=bookcopy_id)
    book_desc = aux.get_book_details(book_copy)
    
    context = {
        'copy' : book_desc,
    }

    if request.method == 'POST':
        post = request.POST
        if 'return' in post:
            aux.return_rental(request.user, post['return'])
            messages.info(request, 'Copy successfully returned')
            
    
    tb_processor = TimeBarRequestProcessor(request, None, config)  # default date range
    tb_context = tb_processor.get_context(book_copy)
    context.update(tb_context)
    
    if not request.user.has_perm('baseapp.list_users'):
        return HttpResponseRedirect(reverse('reserve', args=(bookcopy_id,)))

    rentals = Rental.objects.filter(reservation__book_copy__id=bookcopy_id, end_date=None)
    # assert rentals.count <= 1:
    if rentals.count() > 1:
        utils.get_logger('view.show_book_copy').error('''There are {0} active rentals on book copy with shelf_mark {1}.
                                                         Should be no more than one.'''.format(rental.count(),
                                                                                               book_copy.shelf_mark)
                                                     )
    if rentals and \
       request.user.has_perm('baseapp.change_rental') and \
       request.user in rentals[0].reservation.book_copy.location.maintainer.all():
            context.update({'rental' : rentals[0]})

    return render_response(request, 'bookcopy.html', context)


@login_required
def book_copy_up_link(request, bookcopy_id):
    book_id = get_object_or_404(BookCopy, id=bookcopy_id).book.id
    return HttpResponseRedirect('/entelib/books/%s/' % book_id)


def user_book_copy_up_link(request, user_id, bookcopy_id):
    book_id = get_object_or_404(BookCopy, id=bookcopy_id).book.id
    return HttpResponseRedirect('/entelib/users/%s/books/%s/' % (user_id,  book_id))


@permission_required('baseapp.list_users')
def find_user_to_rent_him(request):
    return show_users(request) 


@permission_required('baseapp.add_book')
def show_add_book(request, edit_form=forms.BookForm):
    if request.method == 'POST':
        form = edit_form(data=request.POST)
        if form.is_valid():
            new_book = form.save()
            messages.info(request, 'Book successfully added.')
            return HttpResponseRedirect(reverse('book_one', args=(new_book.id,)))
    else:
        form = edit_form()
    book_authors = ''
    if 'author' in request.POST:
        book_authors = request.POST['author']
    all_authors = utils.AutocompleteHelper(Author.objects.values_list('name',flat=True).order_by('name')).as_str()
    context = {
        'form'        : form,
        'is_adding'   : True,         # adding new book
        'ac_authors'  : book_authors,
        'all_authors' : all_authors,
        }
    return render_response(request, 'books/one.html', context)

@permission_required('baseapp.change_book')
def show_edit_book(request, book_id, edit_form=forms.BookForm):
    book = get_object_or_404(Book, id=book_id)
    book_authors = utils.AutocompleteHelper(book.author.values_list('name',flat=True).order_by('name')).as_str(delim='')+','
    if request.method == 'POST':
        form = edit_form(data=request.POST, instance=book, initial={'author':'asdfasdfas'})
        book_authors = request.POST['author']
        if form.is_valid():
            form.save()
            messages.info(request, 'Book successfully updated.')
            return HttpResponseRedirect(reverse('book_one', args=(book.id,)))
    else:
        form = edit_form(instance=book, initial={'author':'asdfasdfas'})

    all_authors = utils.AutocompleteHelper(Author.objects.values_list('name',flat=True).order_by('name')).as_str()
    context = {
        'form'        : form,
        'book'        : book,
        'ac_authors'  : book_authors,
        'all_authors' : all_authors,
        'is_updating' : True,        # editing existing book
        }
    return render_response(request, 'books/one.html', context)


@permission_required('baseapp.add_bookcopy')
def show_add_bookcopy(request, book_id, edit_form=forms.BookCopyForm):
    book = get_object_or_404(Book, id=book_id)
    initial_data = { 
        'book' : book.id,
        }
    if request.method == 'POST':
        form = edit_form(data=request.POST, initial=initial_data)
        if form.is_valid():
            new_copy = form.save()
            messages.info(request, 'Book copy successfully added.')
            return HttpResponseRedirect(reverse('copy_one', args=(new_copy.id,)))
    else:
        form = edit_form(initial=initial_data)
    
    context = {
        'form'       : form,
        'book'       : book,
        'is_adding'  : True,    # adding new copy
        }
    return render_response(request, 'copies/one.html', context)

@permission_required('baseapp.change_bookcopy')
def show_edit_bookcopy(request, copy_id, edit_form=forms.BookCopyForm):
    copy = get_object_or_404(BookCopy, id=copy_id)
    if request.method == 'POST':
        form = edit_form(data=request.POST, instance=copy)
        if form.is_valid():
            form.save()
            messages.info(request, 'Book copy successfully updated.')
            return HttpResponseRedirect(reverse('copy_one', args=(copy.id,)))
    else:
        form = edit_form(instance=copy)
    
    context = {
        'form'        : form,
        'book'        : copy.book,
        'copy'        : copy,
        'is_updating' : True,    # editing existing copy
        }
    return render_response(request, 'copies/one.html', context)



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
        request_username         = post['username'].strip() if 'username' in post else ''
        request_email            = post['email'].strip() if 'email' in post else ''
        request_from_my_building = 'from_my_building' in post
        request_building_id      = int(post['building'])
        user_list = []

        # searching for users
        if 'search' in post:
            if not request.user.userprofile or not request.user.userprofile.building:
                request_building_id = 0
            elif request_from_my_building:
                request_building_id = request.user.userprofile.building.id

        # inactive users are listed iff current user has permission to change them, e.g. activate
        show_only_active_users = not request.user.has_perm('auth.change_user')

        user_list = aux.get_users_details_list(request_first_name,
                                               request_last_name,
                                               request_username,
                                               request_email, 
                                               request_building_id, 
                                               active_only=show_only_active_users)

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
            'rows'             : user_list,
            'search'           : search_data,
            'non_found'        : not len(user_list),  # if no users was found were pass True
            'from_my_building' : request_from_my_building,
            })
    return render_response(request, template, context)


@permission_required('auth.add_user')
def add_user(request, registration_form=forms.RegistrationForm):
    return register(request, 'newactiveuser')


@permission_required('baseapp.list_users')
def show_user(request, user_id, redirect_on_success_url='/entelib/users/%d/', profile_edit_form=forms.ProfileEditForm):
    user_id = int(user_id)
    edited_user = get_object_or_404(User, id=user_id)
    return _do_edit_user_profile(request, edited_user, redirect_on_success_url, profile_edit_form)


def _do_edit_user_profile(request, edited_user, redirect_on_success_url='/entelib/users/%d/', profile_edit_form=forms.ProfileEditForm):
    """
    Displays form for editing user's profile.
    
    request.user -- user editing someone's profile (it can be his own profile)
    edited_user -- user, whose profile will be edited.
    """
    if '%d' in redirect_on_success_url:
        redirect_on_success_url = redirect_on_success_url % edited_user.id
    editor = request.user
    form_initial = profile_edit_form.get_initials_for_user(edited_user, editor)
    can_change_profile = editor.id == edited_user.id or editor.has_perm('auth.change_user')
    if request.method == 'POST' and can_change_profile:
        # use data from post to fill form
        form = profile_edit_form(edited_user, editor=editor, data=request.POST, initial=form_initial)
        if form.is_valid():
            # notify data changed and display profile
            form.save()
            messages.success(request, 'Profile details updated.')
            return HttpResponseRedirect(redirect_on_success_url)
    else:
        # no POST implies fresh form with profiles' data
        form = profile_edit_form(edited_user, editor=editor, initial=form_initial)

    # prepare context and render site
    context = profile_edit_form.build_default_context_for_user(edited_user)
    context['form_content'] = form
    context['reader'] = edited_user
    return render_response(request, 'profile.html', context)


@login_required
def edit_user_profile(request, redirect_on_success_url=u'/entelib/profile/', profile_edit_form=forms.ProfileEditForm):
    """ 
    Displays form for editing user's profile, where user means request.user
    """
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
        to_date = utils.today()
        from_date = utils.after_days(-30, since=to_date)
        day_date = utils.today()
        if 'from' in post:
            from_date = utils.str_to_date(post['from'], from_date)
        if 'to' in post:
            to_date = utils.str_to_date(post['to'], to_date)
        if 'day' in post:
            day_date = utils.str_to_date(post['day'], day_date)
        if report_name in ['status', 'lost_books']:   # status requires only one date
            from_date = day_date
        search_data = {
            'from' : unicode(from_date),
            'to'   : unicode(to_date),
            'day'  : unicode(day_date),
            }
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
                # :-2  is used because <input type="image"...> is sent as "btn_sort_location.x" :/
                order_by = [ k[len(btn_sort_prefix):-2] for k in post.keys() if k.startswith(btn_sort_prefix)]
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
def reserve(request, copy_id, non_standard_user_id=False):  # when non_standard_user_id is set then this view allows also renting
    book_copy = get_object_or_404(BookCopy, id=copy_id)
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
        if 'reserve_button' in post:
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
                elif r.start_date:  # from is correct, to isn't
                    raise EntelibWarning('You need to specify reservation end date')
                else:
                    assert False  # flow should never get here: if there is from was incorrect it raised entelib warning
                overlapping_user_reservations = Reservation.objects \
                                                           .filter(Q_reservation_active) \
                                                           .filter(book_copy=book_copy) \
                                                           .filter(for_whom=user) \
                                                           .filter(Q(end_date__gte  =r.start_date)&Q(end_date__lte  =r.end_date) |  # other reservations ends during requested one
                                                                   Q(start_date__gte=r.start_date)&Q(start_date__lte=r.end_date)    # other reservations starts during requested one
                                                                  ) 
                if overlapping_user_reservations.count() > 0:
                    raise EntelibWarning('You have overlapping active reservation on the book.')

            except EntelibWarning, e:
                reserved.update({'error' : str(e)})
            else:
                r.save()
                aux.confirm_reservation(r)

                reserved.update({'ok' : 'ok'})
                reserved.update({'msg' : config.get_str('message_book_reserved') % (r.start_date.isoformat(), r.end_date.isoformat())})
                reserved.update({'from' : r.start_date.isoformat()})
                reserved.update({'to' : r.end_date.isoformat()})
                reserved.update({'reservation' : r.id})
                reserved.update({'send_possible' : aux.internal_post_send_possible(r)})
                messages.info(request, 'Reservation successfull')
        # renting action requested
        elif 'rent_button' in post:
            if not request.user.has_perm('baseapp.add_rental'):
                raise PermissionDenied('User not allowed to rent')
            if not request.user in book_copy.location.maintainer.all():
                raise PermissionDenied('User not allowed to rent book from this location')
            if not aux.is_book_copy_rentable(book_copy):
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
                # don't rent like this:
                #  rental = Rental(reservation=r, start_date=date.today(), who_handed_out=request.user)
                #  rental.save()
                #  mail.made_rental(rental)  # notifications
                aux.rent(r, request.user)
                reserved.update({'msg' : config.get_str('message_book_rented') % r.end_date.isoformat()})
                messages.info(request, config.get_str('message_book_rented') % r.end_date.isoformat())
            except ValueError:
                reserved.update({'error' : 'error - possibly incorrect date format'})
            except EntelibWarning, w:
                reserved.update({'error' : str(w)})
        elif 'reservation_to_send_or_cancel' in post:
            reservation = get_object_or_404(Reservation, id=int(post['reservation_to_send_or_cancel']))
            if not request.user.has_perm('baseapp.change_reservation') and \
               not (request.user.has_perm('baseapp.change_own_reservation') and user == reservation.for_whom):
                raise PermissionDenied('User not allowed to change or cancel this reservation')
            if 'cancel_button' in post:
                reservation.when_cancelled = now()
                reservation.who_cancelled = request.user
                reservation.save()
                reserved.update({'error' : 'Reservation cancelled'})
            if 'send_button' in post:
                reservation = get_object_or_404(Reservation, id=int(post['reservation_to_send_or_cancel']))
                aux.request_shipment(reservation)
                messages.info(request, 'Send-request has been set')
                reserved.update({'msg' : 'Send-request has been set'})
            
    book_desc = aux.get_book_details(book_copy)

    for_whom = aux.user_full_name(non_standard_user_id)
    # if for_whom:
    #     context.update({'user' : User.objects.get(id=non_standard_user_id)})

    context.update({
        'reader_id'       : user.id,
        'copy_id'         : copy_id,
        'copy'            : book_desc,
        'reserved'        : reserved,
        'for_whom'        : for_whom,
        'can_reserve'     : book_copy.state.is_visible and request.user.has_perm('baseapp.add_reservation'),
        'rental_possible' : aux.is_book_copy_rentable(book_copy) and request.user in book_copy.location.maintainer.all(),
    })

    # time bar        
    tb_processor = TimeBarRequestProcessor(request, None, config)  # default date range
    tb_context = tb_processor.get_context(book_copy)
    context.update(tb_context)

    return render_response(request, 'reserve.html', context)


@permission_required('baseapp.change_own_reservation')
def cancel_all_my_reserevations(request):
    return aux.cancel_all_user_reservations(request, request.user)
    # aux.cancel_user_reservations(user=request.user, canceller=request.user)
    # return render_response(request, 'reservations_cancelled.html', {})

@permission_required('baseapp.list_users')
@permission_required('baseapp.change_reservation')
def cancel_all_user_reservations(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return aux.cancel_all_user_reservations(request, user)



@permission_required('baseapp.list_locations')
def show_locations(request):
    locs = Location.objects.select_related().all()
    context = {'rows' : locs,
               }
    return render_response(request, 'locations/list.html', context)

@permission_required('baseapp.view_location')
def show_location(request, loc_id, edit_form=forms.LocationForm):
    try:
        loc_id = int(loc_id)
    except ValueError:
        loc_id = -1   # will cause 404

    location = get_object_or_404(Location, pk=loc_id)
    if request.method == 'POST':
        # drop maintainers if checkbox checked
        if 'no_maintainers' in request.POST:
            mtrs = request.POST.getlist('maintainer')
            for i in range(len(mtrs)):
                mtrs.pop(0)
        # continue editing
        form = edit_form(data=request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.info(request, 'Location successfully updated')
        else:
            # display unchanged info if form's data is not valid
            location = get_object_or_404(Location, pk=loc_id)
    else:
        form = edit_form(instance=location)
    
    context = {
        'loc'          : location,
        'form'         : form,
        'is_updating'  : True,
        }
    
    return render_response(request, 'locations/one.html', context)

@permission_required('baseapp.change_location')
def show_add_location(request, edit_form=forms.LocationForm):
    if request.method == 'POST':
        # drop maintainers if checkbox checked
        if 'no_maintainers' in request.POST:
            maintainers = request.POST.getlist('maintainer')
            for i in range(len(maintainers)):
                maintainers.pop(0)
        # continue editing
        form = edit_form(data=request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Location successfully added')
    else:
        form = edit_form()

    context = {
        'form'        : form,
        'is_adding'   : True,
        }
    return render_response(request, 'locations/one.html', context)


@permission_required('auth.change_user')
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {'activated_user' : user}
    if not user.is_active:
        # print 'user not active!'
        # print user.id
        aux.activate_user(request.user, user)
        return render_response(request, 'registration/user_activated.html', context)
    else:
        return render_response(request, 'registration/user_already_active.html', context)


@permission_required('auth.change_user')
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {'deactivated_user' : user}
    aux.deactivate_user(request.user, user)
    return render_response(request, 'registration/user_deactivated.html', context)


@permission_required('baseapp.add_rental')
def show_shipment_requests(request):
    return aux.show_reservations(request, shipment_requested=True)

                       
@permission_required('baseapp.add_rental')
def show_current_reservations(request, show_all=False):
    only_rentable = not show_all
    return aux.show_reservations(request, only_rentable=only_rentable)

                       
@permission_required('baseapp.change_rental')
def show_current_rentals(request, all_locations=False):
    context = {}

    locations = request.user.location_set.all()  # locations maintained by user
    rentals = Rental.objects.filter(end_date=None).select_related()
    if not all_locations:
        rentals = rentals.filter(reservation__book_copy__location__in=locations)

    if request.method == 'POST':
        post = request.POST
        if 'return' in post:
            rental = get_object_or_404(Rental, id=post['rental_id'])
            aux.return_rental(request.user, rental.id)
            context.update({'message' : 'Accepted returnal of %s (%s) from %s.' % \
                (rental.reservation.book_copy.book.title,
                 rental.reservation.book_copy.shelf_mark,
                 aux.user_full_name(rental.reservation.for_whom)
                )
                })

    rental_list = [
                        { 'id'                : r.id,
                          'user'              : aux.user_full_name(r.reservation.for_whom.id),
                          'start_date'        : r.start_date.date(),
                          'end_date'          : r.reservation.end_date,
                          'location'          : r.reservation.book_copy.location,
                          'shelf_mark'        : r.reservation.book_copy.shelf_mark,
                          'title'             : r.reservation.book_copy.book.title,
                          'authors'           : [a.name for a in r.reservation.book_copy.book.author.all()],
                        } for r in rentals ]
    context.update({ 'rows' : rental_list })
    return render_response(request, 'current_rentals.html', context)


@permission_required('auth.change_user')
def activate_many_users(request, all_inactive=False):
    if request.method == 'POST':
        post = request.POST
        user = get_object_or_404(User, id=post['user_id'])
        if 'activate' in post:
            aux.activate_user(request.user, user)
            messages.info(request, 'User activated')
        elif 'refuse' in post:
            profile = user.userprofile
            profile.awaits_activation = False
            profile.save()
            
    users = User.objects.filter(is_active=False)
    if not all_inactive:
        users = users.filter(userprofile__awaits_activation=True)
    context = {'rows' : users}

    return render_response(request, 'users_awaiting_activation.html', context)


def generic_items(request, name_single, name_plural, query, extra_context={}):
    context = {
        'rows'         : query,
        'name_single'  : name_single,
        'name_plural'  : name_plural,
        }
    context.update(extra_context)
    return render_response(request, '%s/list.html' % name_plural, context)
    
def generic_item(request, name_single, name_plural, item_id, model_name, extra_context={}):
    item = get_object_or_404(model_name, id=item_id)
    context = {
        'item'           : item,
        name_single      : item,
        'is_displaying'  : True,
        'name_single'    : name_single,
        'name_plural'    : name_plural,
        }
    context.update(extra_context)
    return render_response(request, '%s/one.html' % name_plural, context)

def generic_add_item(request, name_single, name_plural, edit_form, model_name, field_name='name', extra_context={}):
    context = {}
    if request.method == 'POST':
        post = request.POST
        form = edit_form(data=post)
        if form.is_valid():
            if 'btn_propositions' in post:
                all_items = list(chain(*model_name.objects.values_list(field_name)))
                propositions = utils.LevenshteinDistance(post[field_name], all_items).most_accurate(15)
                context['propositions'] = propositions
            if ('btn_update' in post) or ('btn_add' in post):
                new_item = form.save()
                messages.info(request, '%s successfully added.' % name_single.capitalize())
                return HttpResponseRedirect(reverse('%s_one' % name_single, args=(new_item.id,)))
    else:
        form = edit_form()
    context.update({
        'form'         : form,
        'is_adding'    : True,         # adding new item
        'name_single'  : name_single,
        'name_plural'  : name_plural,
        })
    context.update(extra_context)
    return render_response(request, '%s/one.html' % name_plural, context)

def generic_edit_item(request, name_single, name_plural, item_id, edit_form, model_name, field_name='name', extra_context={}):
    item = get_object_or_404(model_name, id=item_id)
    context = {}
    if request.method == 'POST':
        post = request.POST
        form = edit_form(data=post, instance=item)
        if form.is_valid():
            if 'btn_propositions' in post:
                all_items = list(chain(*model_name.objects.values_list(field_name)))
                propositions = utils.LevenshteinDistance(post[field_name], all_items).most_accurate(15)
                context['propositions'] = propositions
            if ('btn_update' in post) or ('btn_add' in post):
                form.save()
                messages.info(request, '%s successfully updated.' % name_single.capitalize())
                return HttpResponseRedirect(reverse('%s_one' % name_single, args=(item.id,)))
    else:
        form = edit_form(instance=item)
    context.update({
        'form'         : form,
        'item'         : item,
        name_single    : item,
        'is_updating'  : True,        # editing existing item
        'name_single'  : name_single,
        'name_plural'  : name_plural,
        })
    context.update(extra_context)
    return render_response(request, '%s/one.html' % name_plural, context)

@permission_required('baseapp.list_authors')
def show_authors(request):
    return generic_items(request, 'author', 'authors', Author.objects.all())

@permission_required('baseapp.view_author')
def show_author(request, author_id):
    return generic_item(request, 'author', 'authors', author_id, Author)

@permission_required('baseapp.add_author')
def show_add_author(request, edit_form=forms.AuthorForm):
    return generic_add_item(request, 'author', 'authors', edit_form, Author)

@permission_required('baseapp.change_author')
def show_edit_author(request, author_id, edit_form=forms.AuthorForm):
    return generic_edit_item(request, 'author', 'authors', author_id, edit_form, Author)

@permission_required('baseapp.list_categories')
def show_categories(request):
    return generic_items(request, 'category', 'categories', Category.objects.all())

@permission_required('baseapp.view_category')
def show_category(request, category_id):
    return generic_item(request, 'category', 'categories', category_id, Category)

@permission_required('baseapp.add_category')
def show_add_category(request, edit_form=forms.CategoryForm):
    return generic_add_item(request, 'category', 'categories', edit_form, Category)

@permission_required('baseapp.change_category')
def show_edit_category(request, category_id, edit_form=forms.CategoryForm):
    return generic_edit_item(request, 'category', 'categories', category_id, edit_form, Category)

@permission_required('baseapp.list_buildings')
def show_buildings(request):
    return generic_items(request, 'building', 'buildings', Building.objects.all())

@permission_required('baseapp.view_building')
def show_building(request, building_id):
    return generic_item(request, 'building', 'buildings', building_id, Building)

@permission_required('baseapp.add_building')
def show_add_building(request, edit_form=forms.BuildingForm):
    return generic_add_item(request, 'building', 'buildings', edit_form, Building)

@permission_required('baseapp.change_building')
def show_edit_building(request, building_id, edit_form=forms.BuildingForm):
    return generic_edit_item(request, 'building', 'buildings', building_id, edit_form, Building)

@permission_required('baseapp.list_publishers')
def show_publishers(request):
    return generic_items(request, 'publisher', 'publishers', Publisher.objects.all())
@permission_required('baseapp.view_publisher')
def show_publisher(request, publisher_id):
    return generic_item(request, 'publisher', 'publishers', publisher_id, Publisher)
@permission_required('baseapp.add_publisher')
def show_add_publisher(request, edit_form=forms.PublisherForm):
    return generic_add_item(request, 'publisher', 'publishers', edit_form, Publisher)
@permission_required('baseapp.change_publisher')
def show_edit_publisher(request, publisher_id, edit_form=forms.PublisherForm):
    return generic_edit_item(request, 'publisher', 'publishers', publisher_id, edit_form, Publisher)

@permission_required('baseapp.list_costcenters')
def show_costcenters(request):
    return generic_items(request, 'costcenter', 'costcenters', CostCenter.objects.all())
@permission_required('baseapp.view_costcenter')
def show_costcenter(request, costcenter_id):
    return generic_item(request, 'costcenter', 'costcenters', costcenter_id, CostCenter)
@permission_required('baseapp.add_costcenter')
def show_add_costcenter(request, edit_form=forms.CostCenterForm):
    return generic_add_item(request, 'costcenter', 'costcenters', edit_form, CostCenter)
@permission_required('baseapp.change_costcenter')
def show_edit_costcenter(request, costcenter_id, edit_form=forms.CostCenterForm):
    return generic_edit_item(request, 'costcenter', 'costcenters', costcenter_id, edit_form, CostCenter)

@permission_required('baseapp.list_states')
def show_states(request):
    return generic_items(request, 'state', 'states', State.objects.all())

@permission_required('baseapp.view_state')
def show_state(request, state_id):
    return generic_item(request, 'state', 'states', state_id, State)

@permission_required('baseapp.add_state')
def show_add_state(request, edit_form=forms.StateForm):
    return generic_add_item(request, 'state', 'states', edit_form, State)

@permission_required('baseapp.change_state')
def show_edit_state(request, state_id, edit_form=forms.StateForm):
    return generic_edit_item(request, 'state', 'states', state_id, edit_form, State)

@permission_required('baseapp.list_bookrequests')
def show_bookrequests_active(request):
    return generic_items(request, 'bookrequest', 'bookrequests', BookRequest.objects.filter(done=False).order_by('-when'), extra_context={'displays_only_active':True})

@permission_required('baseapp.list_bookrequests')
def show_bookrequests(request):
    return generic_items(request, 'bookrequest', 'bookrequests', BookRequest.objects.all().order_by('-when'), extra_context={'displays_all':True})

@permission_required('baseapp.view_bookrequest')
def show_bookrequest(request, bookrequest_id):
    return generic_item(request, 'bookrequest', 'bookrequests', bookrequest_id, BookRequest)
# @permission_required('baseapp.add_bookrequest')
# def show_add_bookrequest(request, edit_form=forms.BookRequestForm):
#     return generic_add_item(request, 'bookrequest', 'bookrequests', edit_form, BookRequest)

@permission_required('baseapp.change_bookrequest')
def show_edit_bookrequest(request, bookrequest_id, edit_form=forms.BookRequestForm):
    return generic_edit_item(request, 'bookrequest', 'bookrequests', bookrequest_id, edit_form, BookRequest)

@permission_required('baseapp.add_bookrequest')
def show_add_bookrequest(request, book_id=0, request_form=forms.BookRequestAddForm, extra_context={}):
    """
    Handles requesting for book by any user.

    Args:
        book_id -- if leq 0, then request for book supposed. Otherwise - for book with given id, which should be highlighted.
    """
    book_id = int(book_id)
    requesting_copy = book_id > 0
    user = request.user
    template = 'bookrequests/add.html'
    context = {}
    config = Config(user)
    book = None               # related book if requesting a copy, None otherwise

    if requesting_copy:
        book = get_object_or_404(Book, id=book_id)
        context['related_book'] = book
        info_template = config.get_str('book_request_copyinfo_template')
    else:
        info_template = config.get_str('book_request_bookinfo_template')

    initial_data = {
        'info'         : info_template,
        'book'         : book_id,
        }
    # redisplay form
    if request.method == 'POST':
        form = request_form(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            context['show_confirmation_msg'] = True
            return render_response(request, template, context)
    # display fresh new form
    else:
        form = request_form(user=user, initial=initial_data)
    context.update( {
            'form_content'    : form,
            'books'           : list(Book.objects.all()),
            'requested_items' : list(BookRequest.objects.all()),
            'requesting_copy' : requesting_copy,
            'requesting_book' : not requesting_copy,
            })
    context.update(extra_context)
    return render_response(request, template, context)


def howto(request):
    return render_response(request, 'howto.html')
