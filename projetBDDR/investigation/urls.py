from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'), 
    path('employees', listeEmployees, name='employees'),
    path('emails', listeEmails, name='emails'),
    path('recherche', details_about_employee, name="recherche"),
    path('countEmail', count_mails, name='countEmail'),
    path('rechercheEmployee', search_employee, name='rechercheEmployee'),
    path('rechercheEmployee/dates', dates, name='dates'),
    path('rechercheEmployee/dates/detailsCommunication', employees_communication, name='details'),
    path('coupleEmployees/', couple_employees_ayant_communique, name='coupleEmployees'),
    path('coupleEmployees/detailsCouples/', CoupleCommunicationView.as_view(), name='detailsCouples'),
] 