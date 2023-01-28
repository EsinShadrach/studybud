from django.contrib import admin

# Register your models here.
from .models import (
    Room, Topic, Messages, User
)

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Messages)
admin.site.register(User)