from django.db import models
import re

# Create your models here.
class UserManager(models.Manager):
    def validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        NAME_REGEX = re.compile(r'^[A-Za-z]{2,25}( [A-Za-z]{2,25})?$')
        if len(postData['first_name']) < 2:
            errors['first_name'] = 'First name must be at least 2 characters long'
        if not NAME_REGEX.match(postData['first_name']):
            errors['first_name'] = 'First name invalid'
        if len(postData['last_name']) < 2:
            errors['last_name'] = 'Last name must be at least 2 characters long'
        if not NAME_REGEX.match(postData['last_name']):
            errors['last_name'] = 'Last name invalid'
        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = 'Email must be valid!'
        if not User.objects.filter(email=postData['email']).count() < 1:
            errors['email'] = 'Email must be unique!'
        if len(postData['password']) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        if not postData['password'] == postData['conf_password']:
            errors['conf_password'] = 'Password have to match'
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=150)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class BookManager(models.Manager):
    def validator(self, postData, updating=False):
        errors = {}
        if len(postData['title']) < 1:
            errors['title'] = 'Title is required'
        if Book.objects.filter(title=postData['title']).count() > 0 and not updating:
            errors['title'] = 'Book already in database'
        elif Book.objects.filter(title=postData['title']).count() > 1:
                errors['title'] = 'Book already in database'
        if len(postData['description']) < 5:
            errors['description'] = 'Description must be at least 5 characters'
        return errors

class Book(models.Model):
    uploaded_by = models.ForeignKey(User, related_name="books_uploaded", blank=True, null=True, on_delete=models.SET_NULL)
    users_who_like = models.ManyToManyField(User, related_name="books_liked")
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BookManager()