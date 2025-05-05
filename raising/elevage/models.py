from decimal import Decimal
from random import randint, choice
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Rules(models.Model):
    
    foodPrice = models.IntegerField(default=10) #10€ per kg
    cagePrice = models.IntegerField(default=100)
    rabbitSalePrice = models.IntegerField(default=50)
    medecinePrice = models.IntegerField(default=20) 
    
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
    
    maxPossiblePerCage = models.IntegerField(default=10)
    probMortContamine = models.FloatField(default=0.2)
    probGuerison = models.FloatField(default=0.5)
    
    probContaminaison = models.FloatField(default=0.1)
    
    def __str__(self):
        return "Règles de l'élevage"

class Elevage(models.Model):
    
    nom = models.CharField(max_length=100, default='Partie sans nom')
    
    # Ressources
    nb_males = models.PositiveBigIntegerField(default=1)
    nb_femelles = models.PositiveBigIntegerField(default=1)
    quantite_nourriture = models.DecimalField(default=0, max_digits=100, decimal_places=2)
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
        males = self.getMalesPresent()
        femelles = self.getFemalesPresent()
        nbLapins = males + femelles

        return {
            "nom": self.nom,
            "males": males,
            "femelles": femelles,
            "nbLapins": nbLapins,
            "quantite_nourriture": float(self.quantite_nourriture),
            "nb_cages": self.nb_cages,
            "solde": self.solde,
            "nbTurn": self.nbTurn,
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
        
        if Decimal(totalConsumption) <= self.quantite_nourriture:
            self.quantite_nourriture -= Decimal(totalConsumption)
        else:
            
            #sort the individuals by age and remove the oldest ones first
            sortedIndividuals = sorted(consumptionPerIndividuals, key=lambda x: x[0].age, reverse=True) #reverse=true to sort by age descending
            remainingFood = self.quantite_nourriture
            #Same idea as before, for database safety, I mark the individuals that should die and delete them later out of the loop
            deathsDueToFood = []
            
            for individu, consumption in sortedIndividuals:
                
                if remainingFood >= Decimal(consumption):
                    
                    remainingFood -= Decimal(consumption)
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
        maxPerCage = rules.maxPerCage
        maxPossiblePerCage = rules.maxPossiblePerCage

        if totalIndividus > totalCages * maxPerCage:

            # Probabilité de contamination linéaire générale
            nb_in_cage_moy = totalIndividus / totalCages
            if nb_in_cage_moy > maxPerCage:
                if nb_in_cage_moy >= maxPossiblePerCage:
                    prob = 1.0
                else:
                    prob = (nb_in_cage_moy - maxPerCage) / (maxPossiblePerCage - maxPerCage)
                for individu in self.individus.filter(etat='PRESENT', age__gt=1):
                    if individu.sante.etat == 'SANTE':
                        if randint(0, 100) < int(prob * 100):
                            individu.sante.etat = 'CONTAMINE'
                            individu.sante.save()
        
        for individu in self.individus.filter(etat='PRESENT', age__gt=1):
            if individu.sante.etat == 'CONTAMINE':
                if randint(0, 100) < int(rules.probMortContamine * 100):
                    individu.etat = 'MORT'
                    individu.sante.etat = 'MORT'
                    individu.save()
                    individu.sante.save()
                    
        self.save()
    
    def buy_medicine_and_heal(self, num_medicines):
        """
        Compra medicine e applica la probabilità di guarigione ai conigli malati.
        """
        rules = Rules.objects.first()
        medicine_cost = num_medicines * rules.medecinePrice

        if self.solde < medicine_cost:
            return False, "Pas assez d'argent pour acheter des médicaments."

        self.solde -= medicine_cost
        self.save()

        prob_guerison = rules.probGuerison
        individus_malades = self.individus.filter(sante__etat='CONTAMINE', etat='PRESENT')

        healed_count = 0
        for individu in individus_malades[:num_medicines]:
            if randint(1, 100) <= prob_guerison * 100:  
                individu.sante.etat = 'GUERISON'
                individu.sante.save()
                healed_count += 1

        return True, f"{healed_count} lapins guéris."

    def contaminate_if_any_sick(self):
        rules = Rules.objects.first()

        if self.individus.filter(sante__etat='CONTAMINE', etat='PRESENT').exists():
            prob = rules.probContaminaison

            for individu in self.individus.filter(sante__etat='SANTE', etat='PRESENT'):
                if randint(1, 100) <= prob * 100:
                    individu.sante.etat = 'CONTAMINE'
                    individu.sante.save()

    def heal_guérison(self):
        """
        Trasforma tutti i lapini in stato 'GUERISON' in 'SANTE'.
        """
        individus_en_guerison = self.individus.filter(sante__etat='GUERISON', etat='PRESENT')
        for individu in individus_en_guerison:
            individu.sante.etat = 'SANTE'
            individu.sante.save()

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
    
    
class Sante(models.Model):
    SANTE_CHOICES = [
        ('SANTE', 'En santé'),
        ('GUERISON', 'Guérison'),
        ('CONTAMINE', 'Contamination'),
        ('MORT', 'Mort'),
    ]
    etat = models.CharField(max_length=15, choices=SANTE_CHOICES, default='SANTE')
    individu = models.OneToOneField('Individu', on_delete=models.CASCADE, related_name='sante')

    def __str__(self):
        return f"{self.individu} - {self.get_etat_display()}"

@receiver(post_save, sender=Individu)
def create_sante_for_individu(sender, instance, created, **kwargs):
    if created:
        Sante.objects.get_or_create(individu=instance, defaults={'etat': 'SANTE'})




