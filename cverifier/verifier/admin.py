from django.contrib import admin

from .models import User, Directory

admin.site.register(User)
admin.site.register(Directory)
