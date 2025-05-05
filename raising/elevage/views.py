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
    
    individus_malades = individus.filter(sante__etat='CONTAMINE')  
    individus_en_guerison = individus.filter(sante__etat='GUERISON')  
    individus_morts = elevage.individus.filter(sante__etat='MORT')  
    # actualData = serializers.serialize('json', individus, fields=('id', 'sexe', 'age', 'etat', 'sante'))
    actualData = {
        'model': 'elevage.Elevage',
        'pk' : elevage.pk,
        'fields' :elevage.getFieldsAndValues()

    }

    form = Action()
    message = None

    if request.method == 'POST':
        form = Action(request.POST)
        if form.is_valid():
            action = form.cleaned_data
            nbMales = individus.filter(sexe='M', etat='PRESENT').count()
            nbFemales = individus.filter(sexe='F', etat='PRESENT').count()
            
            if action['SellMales'] > nbMales or action['SellFemales'] > nbFemales:  
                form.add_error(None, "Pas assez de lapins disponibles.")
            else:
                totalAchat = action['BuyCages'] * Rules.objects.first().cagePrice + action['BuyFood'] * Rules.objects.first().foodPrice
                if totalAchat > elevage.solde:  
                    form.add_error(None, "Pas assez d'argent.")
                else:
                    
                    elevage.solde -= totalAchat
                    elevage.nb_cages += action['BuyCages']
                    elevage.quantite_nourriture -= action['BuyFood']
                    elevage.save()
                    
                    
                    soldMales = individus.filter(sexe='M', etat='PRESENT')[:action['SellMales']]
                    soldFemales = individus.filter(sexe='F', etat='PRESENT')[:action['SellFemales']]
                    nbSold = 0
                    
                    for sold in soldMales:
                        sold.etat = 'VENDU'
                        sold.save()
                        elevage.solde += Rules.objects.first().rabbitSalePrice
                        nbSold += 1
                        
                    for sold in soldFemales:
                        sold.etat = 'VENDU'
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
            
            elevage.heal_guérison()        
            elevage.contaminate_if_any_sick()
                    
            if action['BuyMedicine'] > 0:
                success, message = elevage.buy_medicine_and_heal(action['BuyMedicine'])
                if not success:
                    form.add_error(None, message)

            if elevage.individus.filter(etat='PRESENT').count() == 0:
                elevage.delete()
                return redirect('elevage_gameover')

            return redirect('elevage_dashboard', elevage_id=elevage.id)
                    
                    
    return render(request, 'elevage/dashboard.html', {
        'elevage': elevage, 
        'individus': individus, 
        'individus_males': individus_males, 
        'individus_femelles': individus_femelles,
        'individus_malades': individus_malades,
        'individus_en_guerison': individus_en_guerison,
        'individus_morts': individus_morts,
        'form': form, 
        'message': message,  
        'elevage_fields': elevage.getFieldsAndValues(),
        'actualData': actualData,
    })

def liste(request):
    elevages = Elevage.objects.all()
    return render(request, 'elevage/liste.html', {'elevages': elevages})