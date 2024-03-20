from django import forms

class EmployeeSearchForm(forms.Form):
    employee_name_or_email = forms.CharField(label='nom,prénom ou addresse email', max_length=100)
