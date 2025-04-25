from django import forms
from .models import Elevage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ElevageForm(forms.ModelForm):
    
    class Meta:
        model = Elevage
        fields = ['nom', 'nb_males', 'nb_femelles', 'quantite_nourriture', 'nb_cages', 'solde']
        labels = {
            'nom': "Nom de la partie",
            'nb_males': "Nombre de lapins mâles",
            'nb_femelles': "Nombre de lapins femelles",
            'quantite_nourriture': "Quantité de nourriture (kg)",
            'nb_cages': "Nombre de cages",
            'solde': "Solde (€)",
        }
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Ex : Mon élevage stratégique'}),
        }

class Action(forms.Form):
    
    SellMales = forms.IntegerField(min_value=0, required=False, label="Vendre un lapin mâle")
    SellFemales = forms.IntegerField(min_value=0, required=False, label="Vendre un lapin femelle")
    BuyCages = forms.IntegerField(min_value=0, required=False, label="Acheter des cages")
    BuyFood = forms.IntegerField(min_value=0, required=False, label="Acheter de la nourriture")
    
    ## Custom clean method to ensure that "no answer" equals 0 and not "none" for comparison purposes
    def clean(self):
        cleaned_data = super().clean()
        for key in cleaned_data:
            if cleaned_data[key] is None:
                cleaned_data[key] = 0
        return cleaned_data
    
class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]