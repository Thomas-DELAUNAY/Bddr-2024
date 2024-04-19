from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'), 
    path('employees', listeEmployees, name='employees'),
    path('emails', listeEmails, name='emails'),
    path('recherche', details_about_employee, name="recherche"),
    path('echanges', search_employee, name='echanges'),
    path('dates', dates, name='dates'),
    path('details', employees_communication, name='details'),
    path('count', count_mails, name="count"),
    path('dates2', dates2, name='dates2'),
]