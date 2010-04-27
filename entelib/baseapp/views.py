# Create your views here.
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from entelib.baseapp.models import Book, BookCopy
from django.template import RequestContext
from django.contrib import auth
#from django.contrib.auth.decorators import permission_required

def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/entelib/')


def default(request):
    if request.user.is_authenticated():
        return render_to_response('entelib.html', context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/entelib/login/')


#@permission_required('book.can_view')
def list_books(request):
    url = u'/entelib/book/'
    books = []
    for  elem in Book.objects.all():
        books.append({
            'title':elem.title, 
            'url': url + unicode(elem.id) + '/', 
            'authors': [a.name for a in elem.author.all()]
            })
    return render_to_response(
            'book.html',
            {'books': books},
            context_instance=RequestContext(request)
           )

def show_book(request, book_id):
    url = u'/entelib/bookcopy/'
    book = Book.objects.get(id=book_id)
    authors = [a.name for a in book.author.all()]
    copies = BookCopy.objects.filter(book=book_id)
    book_copies = []
    for elem in copies:
        book_copies.append({
            'url': url + unicode(elem.id) + '/',
            'location': elem.location.name,
            'state': elem.state.name,
            'publisher': elem.publisher.name,
            'year' : elem.year,
            'description': elem.description,
            })
    context = {
        'title' : book.title,
        'authors' : authors,
        'items' : book_copies,
        }
    return render_to_response(
        'bookcopies.html',
        {
            'book' : context,
        },
        context_instance=RequestContext(request)
)
        
    
    




