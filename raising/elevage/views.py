from django.shortcuts import render, redirect, get_object_or_404
from .forms import ElevageForm
from .models import Elevage, Individu

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
    individus = elevage.individus.all()
    return render(request, 'elevage/dashboard.html', {'elevage': elevage, 'individus': individus, 'elevage_fields': elevage.getFieldsAndValues()})

def liste(request):
    elevages = Elevage.objects.all()
    return render(request, 'elevage/liste.html', {'elevages': elevages})