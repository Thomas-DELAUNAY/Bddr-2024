from django.contrib import admin
from .models import AddresseEmail, Email,Employee, ReceiversMail

# Register your models here.
admin.site.register(Email)
admin.site.register(Employee)
admin.site.register(ReceiversMail)
admin.site.register(AddresseEmail)