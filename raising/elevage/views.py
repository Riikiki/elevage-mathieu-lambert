from django.shortcuts import render, redirect, get_object_or_404
from .forms import ElevageForm, Action
from .models import Elevage, Individu, Rules
from django.core import serializers

def home(request):
    return render(request, 'elevage/home.html')

def rules(request):
    return render(request, 'elevage/rules.html')

def gameover(request):
    return render(request, 'elevage/gameover.html')

def nouveau(request):
    if request.method == 'POST':
        
        form = ElevageForm(request.POST)
        if form.is_valid():
            
            elevage = form.save()
            
             # Create Individus for males
            for _ in range(elevage.nb_males):
                Individu.objects.create(
                    elevage=elevage,
                    sexe='M',
                    age=3,  # Default to adult
                    etat='PRESENT'
                )

            # Create Individus for females
            for _ in range(elevage.nb_femelles):
                Individu.objects.create(
                    elevage=elevage,
                    sexe='F',
                    age=3,  # Default to adult
                    etat='PRESENT'
                )
                
            return redirect('elevage_dashboard', elevage_id=elevage.id)
        
    else:
        
        form = ElevageForm()

    return render(request, 'elevage/new.html', {'form': form})

def dashboard(request, elevage_id):
    
    elevage = get_object_or_404(Elevage, id=elevage_id)
    individus = elevage.individus.filter(etat='PRESENT')
    individus_males = individus.filter(sexe='M', etat='PRESENT')
    individus_femelles = individus.filter(sexe='F')
    # actualData = serializers.serialize('json', Elevage.objects.filter(pk=elevage_id))
    actualData = {
        'model' : 'elevage.Elevage',
        'pk' : elevage.pk,
        'fields' : elevage.getFieldsAndValues()
    }
    form = Action()
    
    #compare l'age for the males and femelles
    age_distribution = {
        'labels': ['0-3 mois', '4-6 mois', '7-12 mois', '13-18 mois', '19+ mois'],
        'male_data': [
            individus_males.filter(age__lte=3).count(),
            individus_males.filter(age__gt=3, age__lte=6).count(),
            individus_males.filter(age__gt=6, age__lte=12).count(),
            individus_males.filter(age__gt=12, age__lte=18).count(),
            individus_males.filter(age__gt=18).count()
        ],
        'female_data': [
            individus_femelles.filter(age__lte=3).count(),
            individus_femelles.filter(age__gt=3, age__lte=6).count(),
            individus_femelles.filter(age__gt=6, age__lte=12).count(),
            individus_femelles.filter(age__gt=12, age__lte=18).count(),
            individus_femelles.filter(age__gt=18).count()
        ]
    }
    
    if request.method == 'POST':
        
        form = Action(request.POST)
        
        if form.is_valid():
            
            action = form.cleaned_data
            nbMales = individus.filter(sexe='M', etat='PRESENT').count()
            nbFemales = individus.filter(sexe='F', etat='PRESENT').count()
            
            if action['SellMales'] > nbMales or action['SellFemales'] > nbFemales: # Check if we have enough rabbits to sell
                
                form.add_error(None, "Pas assez de lapins disponibles.")
                
            else:
                
                totalAchat = action['BuyCages'] * Rules.objects.first().cagePrice + action['BuyFood'] * Rules.objects.first().foodPrice
                
                if totalAchat > elevage.solde: # Check if we have enough money to buy
                    
                    form.add_error(None, "Pas assez d'argent.")
                    
                else:
                    
                    # Saving new values
                    elevage.solde -= totalAchat
                    elevage.nb_cages += action['BuyCages']
                    elevage.quantite_nourriture -= action['BuyFood']
                    elevage.save()
                    
                    # Updating individus
                    soldMales = individus.filter(sexe='M', etat='PRESENT')[:action['SellMales']]
                    soldFemales = individus.filter(sexe='F', etat='PRESENT')[:action['SellFemales']]
                    nbSold = 0
                    
                    for sold in soldMales:
                        sold.etat = 'VENDU'
                        sold.save()
                        sold.delete()
                        sold.save()
                        elevage.solde += Rules.objects.first().rabbitSalePrice 
                        nbSold += 1
                        
                    for sold in soldFemales:
                        sold.etat = 'VENDU'
                        sold.save()
                        sold.delete()
                        sold.save()
                        elevage.solde += Rules.objects.first().rabbitSalePrice 
                        nbSold += 1
                    
                    elevage.nbSoldRabbits += nbSold
                    elevage.moneyMade += nbSold * Rules.objects.first().rabbitSalePrice
                    elevage.save()
                    
                    elevage.turnAction(action)
                    elevage.save()
                    
                    elevage.nbTurn += 1
                    elevage.save()
                    
                    # Check if the game is over
                    if elevage.individus.filter(etat='PRESENT').count() == 0:
                        elevage.delete()
                        return redirect('elevage_gameover')
                    
                    return redirect('elevage_dashboard', elevage_id=elevage.id)
    elevage_data_graphe=Elevage.objects.all()
    serialized_elevage=serializers.serialize("json",elevage_data_graphe)
              
                    
    return render(request, 'elevage/dashboard.html', {
        'elevage': elevage, 
        'individus': individus, 
        'individus_males': individus_males, 
        'individus_femelles': individus_femelles,
        'form' : form, 
        'actualData': actualData,
        'elevage_fields': elevage.getFieldsAndValues(),
        'elevage_data_graphe':serialized_elevage,
        'age_distribution': age_distribution
        })

def liste(request):
    elevages = Elevage.objects.all()
    return render(request, 'elevage/liste.html', {'elevages': elevages})