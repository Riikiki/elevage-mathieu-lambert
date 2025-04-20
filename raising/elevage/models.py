from random import randint, choice
from django.db import models

class Rules(models.Model):
    
    foodPrice = models.IntegerField(default=10)
    cagePrice = models.IntegerField(default=100)
    rabbitSalePrice = models.IntegerField(default=50)
    
    #Consumption in grammes per month
    
    consumptionFood1Month = models.IntegerField(default=0)
    consumptionFood2Month = models.IntegerField(default=100)
    consumptionFood3Month = models.IntegerField(default=250)
    
    maxRabys = models.IntegerField(default=4)
    maxPerCage = models.IntegerField(default=6)
    maxAge = models.IntegerField(default=25)
    
    minAgeGravide = models.IntegerField(default=6)
    maxAgeGravide = models.IntegerField(default=24)
    gestation = models.IntegerField(default=1)
    
    def __str__(self):
        return "Règles de l'élevage"

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
            if randint(0, 1) == 1:
                nbRabys = randint(1, rules.maxRabys)
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
        for individu in individus:
            individu.age += 1
            individu.save()
            if individu.age > rules.maxAge:
                individu.etat = 'MORT'
                individu.save()
        
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
            
            for individu, consumption in sortedIndividuals:
                
                if remainingFood >= consumption:
                    
                    remainingFood -= consumption
                    self.quantite_nourriture = remainingFood
                    individu.save()
                    
                else:
                    
                    individu.etat = 'MORT'
                    individu.save()  
                        
        self.save()
        
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
            for i in range(totalIndividus - (totalCages * rules.maxPerCage)):
                #the older one dies
                individu =  self.individus.filter(etat='PRESENT').order_by('-age').first()
                individu.etat = 'MORT'
                individu.save()
        
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
    
    # def deleteSoldOrDead(self):
        
    #     sold = self.objects.get(etat='VENDU', elevage=self.elevage).delete()
    #     dead = self.objects.get(etat='MORT', elevage=self.elevage).delete()
        
       

    
    