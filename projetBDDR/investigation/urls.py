from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'), 
    path('employees', listeEmployees, name='employees'),
    path('recherche', details_about_employee, name="recherche"),
    path('echangesEmployees', employees_communication, name='echanges'),

]