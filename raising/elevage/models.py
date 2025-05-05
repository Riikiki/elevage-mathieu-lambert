from random import randint, choice
from django.db import models
from django.contrib.auth.models import User

class Rules(models.Model):
    
    foodPrice = models.IntegerField(default=10) #10€ per kg
    cagePrice = models.IntegerField(default=100)
    rabbitSalePrice = models.IntegerField(default=50)
    
    #Consumption in kilogrammes per month
    
    consumptionFood1Month = models.FloatField(default=0)
    consumptionFood2Month = models.FloatField(default=0.100)
    consumptionFood3Month = models.FloatField(default=0.250)
    
    maxRabys = models.IntegerField(default=4)
    maxPerCage = models.IntegerField(default=6)
    maxAge = models.IntegerField(default=25)
    
    minAgeGravide = models.IntegerField(default=6)
    maxAgeGravide = models.IntegerField(default=24)
    gestation = models.IntegerField(default=1)
    
    def __str__(self):
        return "Règles de l'élevage"

class Elevage(models.Model):
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null= True, blank=True, related_name="elevages")
    nom = models.CharField(max_length=100, default='Elevage Sans nom')

    # Ressources
    nb_males = models.PositiveBigIntegerField(default=1)
    nb_femelles = models.PositiveBigIntegerField(default=1)
    quantite_nourriture = models.FloatField(default=0)
    nb_cages = models.PositiveBigIntegerField(default=1)
    solde = models.IntegerField(default=0)
    
    # Stats
    nbTurn = models.PositiveBigIntegerField(default=0)
    nbSoldRabbits = models.PositiveBigIntegerField(default=0)
    moneyMade = models.BigIntegerField(default=0)

    def __str__(self):
        return self.nom
    
    def getMalesPresent(self):        
        return self.individus.filter(sexe='M', etat='PRESENT').count()
    
    def getFemalesPresent(self):
        return self.individus.filter(sexe='F', etat='PRESENT').count()
    
    def getFieldsAndValues(self):
        
        return {
            "Nom de la partie": self.nom,
            "Lapins mâles": self.getMalesPresent,
            "Lapins femelles": self.getFemalesPresent,
            "Quantité de nourriture": f"{self.quantite_nourriture} kg",
            "Nombre de cages": self.nb_cages,
            "Solde": f"{self.solde} €",
        }
        
    def reproduceRabbits(self, female, rules):
        
        if female.age >= rules.minAgeGravide and female.age <= rules.maxAgeGravide:
            if randint(0, 1) == 1: #50% chance of being pregnant
                nbRabys = randint(1, rules.maxRabys) #Random number of babies between 1 and maxRabys
                for i in range(nbRabys):
                    sexe = choice(['M', 'F'])
                    age = 0
                    etat = 'PRESENT'
                    elevage = self
                    Individu.objects.create(sexe=sexe, age=age, etat=etat, elevage=elevage)
        
    def turnAction(self, action):
        
        rules = Rules.objects.first()
        individus = Individu.objects.filter(etat='PRESENT')
        
        # Age of the individuals
        #for database safety, I mark the individuals that should die and delete themn later out of the loop
        # I don't want to delete them in the loop because it can cause problems with the database (data base is locked)
        deads = []
        
        for individu in individus:
            individu.age += 1
            if individu.age > rules.maxAge:
                individu.etat = 'MORT'
                deads.append(individu.id)
                
        # Saving first ages using batch update        
        Individu.objects.bulk_update(individus, ['age'])
        
        if deads:
            # Delete the dead individuals
            Individu.objects.filter(id__in=deads).update(etat='MORT')
        
        # Refresh the list of individuals
        individus = Individu.objects.filter(etat='PRESENT')
        
        
        # Consumption of food
        totalConsumption = 0
        consumptionPerIndividuals = []
        
        for individu in individus:
            if individu.age == 1:
                consumption = rules.consumptionFood1Month
            elif individu.age == 2:
                consumption = rules.consumptionFood2Month
            else:
                consumption = rules.consumptionFood3Month
        
            consumptionPerIndividuals.append((individu, consumption))
            totalConsumption += consumption
        
        if totalConsumption <= self.quantite_nourriture:
            self.quantite_nourriture -= totalConsumption
        else:
            
            #sort the individuals by age and remove the oldest ones first
            sortedIndividuals = sorted(consumptionPerIndividuals, key=lambda x: x[0].age, reverse=True) #reverse=true to sort by age descending
            remainingFood = self.quantite_nourriture
            #Same idea as before, for database safety, I mark the individuals that should die and delete them later out of the loop
            deathsDueToFood = []
            
            for individu, consumption in sortedIndividuals:
                
                if remainingFood >= consumption:
                    
                    remainingFood -= consumption
                    self.quantite_nourriture = remainingFood
                    
                else:
                    
                    deathsDueToFood.append(individu.id)
                        
            if deathsDueToFood:
                # Delete the individuals that died due to food
                Individu.objects.filter(id__in=deathsDueToFood).update(etat='MORT')
        
        # Reproduction
        females = self.individus.filter(sexe='F', etat='PRESENT')
        males = self.individus.filter(sexe='M', etat='PRESENT')
        
        MFDiff = females.count() - males.count()
        
        if MFDiff == 0:
    
            for female in females:
                self.reproduceRabbits(female, rules)
        
        else:
            
            nbCouple = females.count() - abs(MFDiff) 
            counter = 0
            for female in females:
                if counter == nbCouple:
                    break
                self.reproduceRabbits(female, rules)
                counter += 1
            
                        
        # Maximum number of individuals in a cage
        totalCages = self.nb_cages
        totalIndividus = self.individus.filter(etat='PRESENT', age__gt=1).count()
        if totalIndividus > totalCages * rules.maxPerCage:
            # Remove the excess individuals
            excess = totalIndividus - totalCages * rules.maxPerCage
            toKill = self.individus.filter(etat='PRESENT').order_by('-age')[:excess]
            idToKill = [individu.id for individu in toKill]
            Individu.objects.filter(id__in=idToKill).update(etat='MORT')
        
        self.save()
          

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
    