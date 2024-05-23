from django import forms


class EmployeeSearchForm(forms.Form):
    employee_name_or_email = forms.CharField(label='nom,prénom ou addresse email', max_length=100)

class CountEmailsForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin")   
    nombre_min = forms.IntegerField(label="Nombre minimum de mails") 
    nombre_max = forms.IntegerField(label="Nombre maximum de mails") 
   

class CommunicationSearchForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin")
    
 
class CoupleEmployeesForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin") 
    seuil = forms.IntegerField(label="seuil") 
      
class SearchDayWithMoreExchangesForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    date_fin = forms.DateField(label="Date de fin")
    
    
class SearchEmailByWordsForm(forms.Form):
    liste = forms.CharField()
    affichage_par = forms.ChoiceField(label="Affichage par", choices=[("option1", "expéditeur"), ("option2", "destinataire(s)"), ("option3","sujet")])
    
class HotSubjectsForm(forms.Form):
    start_date = forms.DateField(label="Date de début")
    end_date = forms.DateField(label="Date de fin")
    
class SearchHotSubjectsForm(forms.Form):
    sujet = forms.ChoiceField(choices=[], required=True, label="Sujet")

    def __init__(self, *args, **kwargs):
        sujets = kwargs.pop('sujets', [])
        super(SearchHotSubjectsForm, self).__init__(*args, **kwargs)
        self.fields['sujet'].choices = [(sujet, sujet) for sujet in sujets]

class SeuilForm(forms.Form):
    seuil = forms.IntegerField(label="Nombre de sujets à afficher", min_value=1)   