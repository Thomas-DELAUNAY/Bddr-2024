from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'), 
    path('employees', listeEmployees, name='employees'),
    path('recherche', details_about_employee, name="recherche"),
    path('echanges', search_employee, name='echanges'),
    path('dates', dates, name='dates'),
    path('details', employees_communication, name='details'),
]