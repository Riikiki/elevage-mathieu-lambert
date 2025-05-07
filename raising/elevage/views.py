from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ElevageForm, Action, InscriptionForm
from .models import Elevage, Individu, Rules, UserProfile
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    
    print (f"profile={profile}")
    return render(request, 'elevage/home.html', {
    })

def rules(request):
    rules = Rules.objects.first()
    rules = {
    'probGuerison': rules.probGuerison * 100,
    'probMortContamine': rules.probMortContamine * 100,
    'probContamination': rules.probContaminaison * 100,
    'maxPerCage': rules.maxPerCage,
    'maxPossiblePerCage': rules.maxPossiblePerCage,
}
    return render(request, 'elevage/rules.html', {'rules': rules})

def gameover(request):
    return render(request, 'elevage/gameover.html')

def nouveau(request):
    if request.method == 'POST':
        
        form = ElevageForm(request.POST)
        if form.is_valid():
            
            elevage = form.save(commit=False)
            if request.user.is_authenticated:
                elevage.utilisateur = request.user
            elevage.save()
            
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
    female_Gravide = individus.filter(sexe='F', age__gte=6);
    # actualData = serializers.serialize('json', Elevage.objects.filter(pk=elevage_id))
    actualData = {
        'model' : 'elevage.Elevage',
        'pk' : elevage.pk,
        'fields' : elevage.getFieldsAndValues()
    }
    form = Action()
    
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
                    
            #noting the date of selling for every tour
            if action['SellFemales']>0 or action['SellFemales']>0:
                elevage.log_turn('sale',{
                        'males_sold':action['SellMales'],
                        'females_sold':action['SellFemales']
                    })
            #noting the date of birth for every tour
            new_births = Individu.objects.filter(elevage=elevage, age=0).count()
            if new_births > 0:
                elevage.log_turn('birth', {'count': new_births})
            #noting the date of death for every tour
            deaths = Individu.objects.filter(elevage=elevage, etat='MORT').count()
            if deaths > 0:
                elevage.log_turn('death', {'count': deaths})
            ##noting the date of changement of food for every tour
            if action['BuyFood'] > 0:
                elevage.log_turn('food', {
                    'change': action['BuyFood'],
                    'total': elevage.quantite_nourriture
                    })
            ##noting the date of the changement of cages for every tour
            if action['BuyCages'] > 0:
                elevage.log_turn('cage', {
                    'change': action['BuyCages'],
                    'total': elevage.nb_cages
                    })
            
            # Check if the game is over
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
        'elevage_fields': elevage.getFieldsAndValues(),
        'age_distribution': age_distribution
        })

@login_required
def liste(request):
    elevages = Elevage.objects.filter(utilisateur=request.user)
    return render(request, 'elevage/liste.html', {'elevages': elevages})

def login(request):
    return render(request, 'registration/login.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

def connexion(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            profile = UserProfile.objects.get(user=request.user)
            return render(request, 'elevage/home.html', {
            'userpicture': 'elevage/'+profile.profile_picture })
        
        else:
            return render(request, 'registration/connexion.html', {'error': 'Identifiants invalides.'})
    else:
        return render(request, 'registration/connexion.html')


def inscription(request):
    
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            selected_image = request.POST.get('selected_image')
            auth_login (request, user)
            UserProfile.objects.create(
                user=user,
                profile_picture=selected_image
            )
            profile = UserProfile.objects.get(user=request.user)
            return render(request, 'elevage/home.html', {
            'userpicture': 'elevage/'+profile.profile_picture })
        else:
            return render(request, 'elevage/inscription.html', {
                'form': form,
            })
    else:
        form = InscriptionForm()
        return render(request, 'elevage/inscription.html', {'form': form})
