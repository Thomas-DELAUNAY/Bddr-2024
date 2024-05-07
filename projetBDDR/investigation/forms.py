from django import forms


class EmployeeSearchForm(forms.Form):
    employee_name_or_email = forms.CharField(label='nom,prénom ou addresse email', max_length=100)

class CommunicationSearchForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin")
    
class CountEmailsForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin")   
    nombre_min = forms.IntegerField(label="Nombre minimum de mails") 
    nombre_max = forms.IntegerField(label="Nombre maximum de mails") 
    
class CoupleEmployeesForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin") 
    seuil = forms.IntegerField(label="seuil") 
    nombre_max = forms.IntegerField(label="nombre_max")