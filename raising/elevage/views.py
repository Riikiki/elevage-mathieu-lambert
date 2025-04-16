from django.shortcuts import render, redirect, get_object_or_404
from .forms import ElevageForm
from .models import Elevage

def nouveau(request):
    if request.method == 'POST':
        
        form = ElevageForm(request.POST)
        if form.is_valid():
            
            elevage = form.save()
            return redirect('elevage_dashboard', elevage_id=elevage.id)
        
    else:
        
        form = ElevageForm()

    return render(request, 'elevage/new.html', {'form': form})

def dashboard(request, elevage_id):
    elevage = get_object_or_404(Elevage, id=elevage_id)

    return render(request, 'elevage/dashboard.html', {'elevage': elevage})