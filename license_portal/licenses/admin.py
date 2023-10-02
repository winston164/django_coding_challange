from django.contrib import admin

# Register your models here.
from .models import (
    License, 
    Client,
    Notification,
    NotifyRequest
)

admin.site.register(License)
admin.site.register(Client)
admin.site.register(Notification)
admin.site.register(NotifyRequest)
