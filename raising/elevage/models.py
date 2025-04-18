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
        
        

class Individu(models.Model):
    
    sexe = models.CharField(max_length=10, choices=[('M', 'Mâle'), ('F', 'Femelle')])
    age = models.IntegerField(default=0)
    etat = models.CharField(max_length=20, choices=[('PRESENT', 'Présent'),  ('VENDU', 'Vendu'), ('MORT', 'Mort'), ('GRAVIDE', 'Gravide')])
    elevage = models.ForeignKey(Elevage, on_delete=models.CASCADE, related_name='individus')
    
    def __str__(self):
        return self.sexe + " " + str(self.age) + " " + self.etat
    
    def getFieldsAndValues(self):
        
        return {
            "Sexe": self.sexe,
            "Age": self.age,
            "État": self.etat,
        }
    