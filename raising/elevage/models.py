from django.db import models

class Elevage(models.Model):
    
    nom = models.CharField(max_length=100, default='Partie sans nom')
    
    # Resources
    nb_males = models.IntegerField(default=0)
    nb_femelles = models.IntegerField(default=0)
    quantite_nourriture = models.IntegerField(default=0)
    nb_cages = models.IntegerField(default=0)
    solde = models.IntegerField(default=0)

    def __str__(self):
        return self.nom

