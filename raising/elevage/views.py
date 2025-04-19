from django.shortcuts import render, redirect, get_object_or_404
from .forms import ElevageForm, Action
from .models import Elevage, Individu, Rules

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
    form = Action()
    
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
                    
                    for sold in soldMales:
                        sold.etat = 'VENDU'
                        sold.save()
                        sold.delete()
                        sold.save()
                        elevage.solde += Rules.object.first().rabbitSalePrice 
                    for sold in soldFemales:
                        sold.etat = 'VENDU'
                        sold.save()
                        sold.delete()
                        sold.save()
                        elevage.solde += Rules.object.first().rabbitSalePrice 
                    
                    elevage.save()
                    elevage.turnAction(action)
                    elevage.save()
                    return redirect('elevage_dashboard', elevage_id=elevage.id)
                    
    return render(request, 'elevage/dashboard.html', {'elevage': elevage, 'individus': individus, 'form' : form, 'elevage_fields': elevage.getFieldsAndValues()})

def liste(request):
    elevages = Elevage.objects.all()
    return render(request, 'elevage/liste.html', {'elevages': elevages})