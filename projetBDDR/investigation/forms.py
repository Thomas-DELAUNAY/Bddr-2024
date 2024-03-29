from django import forms
from .models import Employee

class EmployeeSearchForm(forms.Form):
    employee_name_or_email = forms.CharField(label='nom,prénom ou addresse email', max_length=100)

class CommunicationSearchForm(forms.Form):
    #employee = forms.CharField(label='nom,prénom ou addresse email', max_length=100)
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin")
    
