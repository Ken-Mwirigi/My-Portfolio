# admin.py
from django.contrib import admin
from .models import ContactMessage

# Register the ContactMessage model
admin.site.register(ContactMessage)
