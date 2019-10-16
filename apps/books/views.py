from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import bcrypt

# Create your views here.
def index(request):
    return render(request, "books/index.html")

def register(request):
    loc = "/"
    if 'id' in request.session:
        messages.error(request, 'You are already logged in')
        return redirect(loc)
    if request.method == 'POST' and 'email' in request.POST and 'password' in request.POST and 'conf_password' in request.POST and 'first_name' in request.POST and 'last_name' in request.POST:
        errors = User.objects.validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
        else:
            hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
            new_user = User.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=hashed)
            request.session['id'] = new_user.id
            request.session['first_name'] = new_user.first_name.capitalize()
            loc = "/books"
    return redirect(loc)

def login(request):
    loc = "/"
    if 'id' in request.session:
        messages.error(request, 'You are already logged in')
        return redirect(loc)
    if request.method == 'POST' and 'lemail' in request.POST and 'lpassword' in request.POST:
        if not User.objects.filter(email=request.POST['lemail']).count() == 1:
            messages.error(request, 'Invalid login combination')
        else:
            if bcrypt.checkpw(request.POST['lpassword'].encode(), User.objects.get(email=request.POST['lemail']).password.encode()):
                user = User.objects.get(email=request.POST['lemail'])
                request.session['id'] = user.id
                request.session['first_name'] = user.first_name.capitalize()
                loc = "/books"
            else:
                messages.error(request, 'Invalid login combination')
    return redirect(loc)

def logout(request):
    loc = "/"
    if 'id' in request.session:
        request.session.clear()
        messages.success(request, 'Successfully logged out')
    return redirect(loc)

def books(request):
    if not 'id' in request.session or User.objects.filter(id=request.session['id']).count() != 1:
        messages.error(request, 'Not logged in')
        return redirect("/")
    content = {
        'books': Book.objects.all(),
        'user': User.objects.get(id=request.session['id'])
    }
    return render(request, "books/books.html", content)

def add(request):
    loc = "/books"
    if not 'id' in request.session:
        messages.error(request, 'Not logged in')
        loc = "/"
    else:
        if request.method == 'POST' and 'title' in request.POST and 'description' in request.POST:
            errors = Book.objects.validator(request.POST)
            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value, extra_tags=key)
            else:
                user = User.objects.get(id=request.session['id'])
                new_book = Book.objects.create(uploaded_by=user, title=request.POST['title'], description=request.POST['description'])
                user.books_liked.add(new_book)
                messages.success(request, 'Successfully added book')
    return redirect(loc)

def book(request, id):
    if not 'id' in request.session:
        messages.error(request, 'Not logged in')
        return redirect("/")
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        messages.error(request, 'Book does not exist')
        return redirect("/books")
    content = {
        'book': book,
        'user': User.objects.get(id=request.session['id'])
    }
    return render(request, "books/book.html", content)

def favorite(request, id):
    loc = "/books"
    if not 'id' in request.session:
        messages.error(request, 'Not logged in')
        return redirect("/")
    if Book.objects.filter(id=id).count() == 1:
        loc = f"/books/{id}"
        if User.objects.filter(id=request.session['id']).count() == 1:
            user = User.objects.get(id=request.session['id'])
            book = Book.objects.get(id=id)
            if not book in user.books_liked.all():
                user.books_liked.add(book)
                messages.success(request, 'Successfully added book to favorites')
            else:
                messages.error(request, 'Book already in your favorites')
        else:
            messages.error(request, 'Session data corrupt')
    else:
        messages.error(request, 'Unable to locate book')
    return redirect(loc)

def unfavorite(request, id):
    loc = "/books"
    if not 'id' in request.session:
        messages.error(request, 'Not logged in')
        return redirect("/")
    if Book.objects.filter(id=id).count() == 1:
        loc = f"/books/{id}"
        if User.objects.filter(id=request.session['id']).count() == 1:
            user = User.objects.get(id=request.session['id'])
            book = Book.objects.get(id=id)
            if book in user.books_liked.all():
                user.books_liked.remove(book)
                messages.success(request, 'Successfully removed book from your favorites')
            else:
                messages.error(request, 'Book not favorited')
        else:
            messages.error(request, 'Session data corrupt')
    else:
        messages.error(request, 'Unable to locate book')
    return redirect(loc)

def update(request, id):
    loc = "/books"
    if not 'id' in request.session:
        messages.error(request, 'Not logged in')
        return redirect("/")
    if request.method == 'POST' and 'title' in request.POST and 'description' in request.POST:
        if Book.objects.filter(id=id).count() == 1:
            loc = f"/books/{id}"
            if User.objects.filter(id=request.session['id']).count() == 1:
                user = User.objects.get(id=request.session['id'])
                book = Book.objects.get(id=id)
                if book.uploaded_by == user:
                    errors = Book.objects.validator(request.POST, True)
                    if len(errors) > 0:
                        for key, value in errors.items():
                            messages.error(request, value, extra_tags=key)
                    else:
                        book.title = request.POST['title']
                        book.description = request.POST['description']
                        book.save()
                        messages.success(request, 'Successfully updated book')
                else:
                    messages.error(request, 'Insufficient permission')
            else:
                messages.error(request, 'Session data corrupt')
        else:
            messages.error(request, 'Unable to locate book')
    return redirect(loc)

def delete(request, id):
    loc = "/books"
    if not 'id' in request.session:
        messages.error(request, 'Not logged in')
        return redirect("/")
    if Book.objects.filter(id=id).count() == 1:
        loc = f"/books/{id}"
        if User.objects.filter(id=request.session['id']).count() == 1:
            user = User.objects.get(id=request.session['id'])
            book = Book.objects.get(id=id)
            if book.uploaded_by == user:
                book.delete()
                messages.success(request, 'Successfully deleted book')
                loc = "/books"
            else:
                messages.error(request, 'Insufficient permission')
        else:
            messages.error(request, 'Session data corrupt')
    else:
        messages.error(request, 'Unable to locate book')
    return redirect(loc)

def user(request):
    if not 'id' in request.session:
        messages.error(request, 'Not logged in')
        return redirect("/")
    content = {
        'books': User.objects.get(id=request.session['id']).books_liked.all(),
        'user': User.objects.get(id=request.session['id'])
    }
    return render(request, "books/user.html", content)