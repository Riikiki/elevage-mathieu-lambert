from django.contrib import admin
from .models import Elevage, Individu


admin.site.register(Elevage)
admin.site.register(Individu)


class ElevageAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'nom', 'nb_males', 'nb_femelles', 'quantite_nourriture', 'nb_cages', 'solde', 'date_creation')
    search_fields = ('nom',)
