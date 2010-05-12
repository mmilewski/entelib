#-*- coding=utf-8 -*-

# Create your views here.
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from entelib.baseapp.models import *   # Book, BookCopy
from django.template import RequestContext
from django.contrib import auth
from django.db.models import Q
from views_aux import render_forbidden
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
    if request.user.is_authenticated():
        return render_to_response('entelib.html', context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/entelib/login/')


#TODO jakieś bardziej zaawansowane wyszukiwanie
def list_books(request):
    url = u'/entelib/books/'
    books = []
    if request.user.is_authenticated():
        if request.method == 'POST':
            search_words = request.POST['search'].split()
            if search_words:

                def format_search_request(keywords):
                    return reduce(lambda x, y: Q(title__icontains=x) and Q(title__icontains=y), keywords, Q(title__contains=u''))
                for elem in Book.objects.filter(format_search_request(search_words)):
                    books.append({
                        'title': elem.title,
                        'url': url + unicode(elem.id) + '/',
                        'authors': [a.name for a in elem.author.all()]
                        })
        return render_to_response(
                'book.html',
                {'books': books},
                context_instance=RequestContext(request)
               )
    else:
        return render_forbidden(request)


def show_book(request, book_id):
    if request.user.is_authenticated():
        url = u'/entelib/bookcopy/'
        book = Book.objects.get(id=book_id)
        copies = BookCopy.objects.filter(book=book_id)
        if request.method == 'POST':
            if 'location' in request.POST:
                if not request.POST['location'] == u'0':
                    copies = copies.filter(location__exact=request.POST['location'])
            if 'available' in request.POST:
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
        return render_to_response(
            'bookcopies.html',
            {
                'book' : book_desc,
            },
            context_instance=RequestContext(request)
        )
    else:
        return render_forbidden(request)


#TODO wszystko poniżej jest draftem z czasu zanim adi zamieścił templaty
#     Ja to dokończę
#     mbr
def book_copy(request, bookcopy_id):
    if request.user.is_authenticated():
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
        return render_to_response(
            'bookcopy.html',
            {
                'book' : book_desc,
                'can_reserve' : request.user.has_perm('basapp.add_reservation'),
                #'can_rent' : request.user.has_perm('baseapp.add_rental'), and  #TODO
                #'can_return' : request.user.has_perm('baseapp.change_rental'), #TODO
            },
            context_instance=RequestContext(request)
        )
    else:
        return render_forbidden(request)


'''

def users(request):
    user_request = request.POST['request']
    user_list = []
    if user_request:
        user_list = [ {'last_name': u.last_name, 'first_name': u.first_name, 'email': u.email,'url': u.id + '/'}
                      for u in User.objects.all() ] #TODO FILTROWANIE!
    return render_to_response(
        'users.html',
        { 'user_list' : user_list, },
        context_instance=RequestContext(request)
    )


def user(request, user_id):
    user = User.objects.get(id=user_id)
    return render_to_response(
        'user.html',
        { 'first_name' : user.first_name,
          'last_name' : user.last_name,
          'email' : user.email,
          },
        context_instance=RequestContext(request)
    )

def users_rentals(request, user_id):
    user = User.objects.get(id=user_id)
    users_rentals = user. #TODO jego wypożyczenia (aktywne)
    rent_list = [ {'id': r.reservation.book_copy.id, 'title': r.reservation.book_copy.book.title, }
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



def users_rental(request, user_id, rental_id):
    user = User.objects.get(id=user_id)
    rental = Rental.objects.get(id=rental_
'''
