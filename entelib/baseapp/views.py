#-*- coding=utf-8 -*- 

# Create your views here.
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from entelib.baseapp.models import * #Book, BookCopy
from django.template import RequestContext
from django.contrib import auth
from django.db.models import Q
from views_aux import render_forbidden, render_response
from config import Config
#from django.contrib.auth.decorators import permission_required
from baseapp.forms import RegistrationForm




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
            return render_to_response(tpl_logout_first, context_instance=RequestContext(request))
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
                                      { 'form_content': form },
                                      context_instance=context)


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/entelib/')


def default(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/entelib/login/')
    return render_response(request, 'entelib.html')


def list_books(request):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    url = u'/entelib/books/'
    books = []
    if request.method == 'POST':
        search_words = request.POST['search'].split()
        if search_words:
            def format_search_request(keywords, all=True):
                if all: # search for titles with all keywords
                    return reduce(lambda x,y: Q(title__icontains=x) and Q(title__icontains=y), keywords, Q(title__contains=u''))
                else:   # search for titles with any of keywords
                    return reduce(lambda x,y: Q(title__icontains=x) or Q(title__icontains=y), keywords, Q(id__exact=u''))
            for elem in Book.objects.filter(format_search_request(search_words)):
                books.append({
                    'title':elem.title, 
                    'url': url + unicode(elem.id) + '/', 
                    'authors': [a.name for a in elem.author.all()]
                    })
    return render_response(request, 'book.html', {'books': books}) 



def show_book(request, book_id):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    url = u'/entelib/bookcopy/'
    book = Book.objects.get(id=book_id)
    copies = BookCopy.objects.filter(book=book_id)
    if request.method == 'POST':
        if 'location' in request.POST:
            if not request.POST['location'] == u'0':
                copies = copies.filter(location__exact=request.POST['location'])
        if r'available' in equest.POST:
            if request.POST['available'] == 'available':
                copies = copies.filter(state__is_available__exact=True)
                print request.POST
    book_copies = []
    max_desc_len = Config().get_int('truncated_description_len')
    for elem in copies:
        book_copies.append({
            'url': url + unicode(elem.id) + '/',
            'location': elem.location.name,
            'state': elem.state.name,
            'publisher': elem.publisher.name,
            'year' : elem.year,
            'description': elem.description[:max_desc_len],
            })
    book_desc = {
        'title' : book.title,
        'authors' : [a.name for a in book.author.all()],
        'items' : book_copies,
        'locations' : [{'name': '---', 'id': 0}] + [{'name': l.name, 'id': l.id} for l in Location.objects.all()] 
        }
    return render_response(request, 'bookcopies.html', { 'book' : book_desc, })



#TODO can_rent i can_return
def book_copy(request, bookcopy_id):
    if not request.user.is_authenticated():
        return render_forbidden(request)
    book_copy = BookCopy.objects.get(id=bookcopy_id)
    book = book_copy.book
    book_desc = {
        'title' : book.title,
        'authors' : [a.name for a in book.author.all()],
        'location': book_copy.location.name,
        'state': book_copy.state.name,
        'publisher': book_copy.publisher.name,
        'year' : book_copy.year,
        'description': book_copy.description,
        'picture' : book_copy.picture,
        }
    return render_response(request, 'bookcopy.html',
        {
            'book' : book_desc,
            'can_reserve' : request.user.has_perm('baseapp.add_reservation'),
            #'can_rent' : request.user.has_perm('baseapp.add_rental'), and  #TODO
            #'can_return' : request.user.has_perm('baseapp.change_rental'), #TODO
        }
    )
        

   
def users(request):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    if request.method == 'POST':
        request_first_name = request.POST['first_name'] if request.POST.has_key('first_name') else ''
        request_last_name = request.POST['last_name'] if request.POST.has_key('last_name') else ''
        request_email = request.POST['email'] if request.POST.has_key('email') else ''
        user_list = []
        if request.POST.has_key('action') and request.POST['action'] == 'Search':
            user_list = [ {'last_name': u.last_name, 'first_name': u.first_name, 'email': u.email,'url': unicode(u.id) + u'/'}
                          for u in User.objects.filter(first_name__icontains=request_first_name).filter(last_name__icontains=request_last_name).filter(email__icontains=request_email) ]
        dict = { 
            'users' : user_list, 
            'first_name' : request_first_name,
            'last_name' : request_last_name,
            'email' : request_email,
            }
    else:
        dict = {}
    return render_response(request, 'users.html', dict)

        
        
def user(request, user_id):
    user = User.objects.get(id=user_id)
    return render_response(request, 'user.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email, 
        }
    )


def user_rentals(request, user_id):
    if not request.user.is_authenticated() or not request.user.has_perm('baseapp.list_users'):
        return render_forbidden(request)
    user = User.objects.get(id=user_id)
    users_rentals = Rental.objects.filter(reservation__for_whom=user.id).filter(who_received__isnull=True)
    rent_list = [ {'id': r.reservation.book_copy.magic_number, 'title': r.reservation.book_copy.book.title, }
                    for r in users_rentals ] 
    return render_to_response(
        'users_rentals.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email, 
          'rentals' : rent_list,
          },
        context_instance=RequestContext(request)
    )

'''

        
def users_rental(request, user_id, rental_id):
    user = User.objects.get(id=user_id)
    rental = Rental.objects.get(id=rental_
'''



