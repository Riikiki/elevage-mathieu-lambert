from django import forms
from .models import Elevage

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
    
    action = forms.ChoiceField(
        choices=[
            ('vendre un lapin mâle', 'VendreMâle'),
            ('vendre un lapin femelle', 'VendreFemelle'),
            ('acheter nouriture', 'AcheterNourriture'),
            ('acheter cage', 'AcheterCage'),
        ],
        
        label="Action à effectuer",
        widget=forms.Select(attrs={'class': 'form-control'})
        
    )