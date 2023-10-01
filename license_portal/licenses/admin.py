from django.contrib import admin

# Register your models here.
from .models import License, Client

admin.site.register(License)
admin.site.register(Client)
