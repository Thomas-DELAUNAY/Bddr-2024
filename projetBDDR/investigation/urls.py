from django.urls import path
from .views import *

urlpatterns = [
    path('', page_accueil, name='accueil'),
    path('accueil', index, name='index'), 
    path('employees', listeEmployees, name='employees'),
    path('addresseemails', listeAddresseEmail, name='addresseemails'),
    path('recherche', recherche_employees, name="recherche"),
    path('countEmail', count_mails, name='countEmail'),
    path('countEmail/<str:addresse_email>', infos_sur_employee, name="infosEmployee"),
    path('rechercheEmployee', search_employee, name='rechercheEmployee'),
    path('rechercheEmployee/dates', dates, name='dates'),
    path('rechercheEmployee/dates/detailsCommunication', employees_communication, name='details'),
    path('coupleEmployees/', couple_employees_ayant_communique, name='coupleEmployees'),
    path('coupleEmployees/detailsCouples/', CoupleCommunicationView.as_view(), name='detailsCouples'),
    path('rechercheDay/', jour_avec_plus_echanges, name="searchdaydetails"),
    path('rechercheEmail/', recherche_par_mots, name="rechercheEmail"),
    path('rechercheEmail/contenuEmail/<int:email_id>/', afficher_contenu_email, name="contenuEmail"),
    path('HotSubjects', hot_subjects, name='hotSubjects'),
    path('employesSuspects', employees_avec_plus_messages_externes, name="suspects"),

] 