from django.urls import path,include
from .views import *

urlpatterns = [
    #path('index', views.index, name='index'), 
    path('', index, name='index'), 
    path('clients', listeClients, name='employees'),
    path('recherche', employee_details, name="recherche"),
    path('infos/<str:name>', details_about_employee, name="infos")

]