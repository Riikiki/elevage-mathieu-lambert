from django.db import models

class Elevage(models.Model):
    
    nom = models.CharField(max_length=100, default='Partie sans nom')
    
    # Ressources
    nb_males = models.IntegerField(default=0)
    nb_femelles = models.IntegerField(default=0)
    quantite_nourriture = models.IntegerField(default=0)
    nb_cages = models.IntegerField(default=0)
    solde = models.IntegerField(default=0)

    def __str__(self):
        return self.nom
    
    def getFieldsAndValues(self):
        
        return {
            "Nom de la partie": self.nom,
            "Lapins mâles": self.nb_males,
            "Lapins femelles": self.nb_femelles,
            "Quantité de nourriture": f"{self.quantite_nourriture} kg",
            "Nombre de cages": self.nb_cages,
            "Solde": f"{self.solde} €",
        }

