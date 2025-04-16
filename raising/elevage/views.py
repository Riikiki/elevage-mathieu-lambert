from django.shortcuts import render, redirect
from .forms import ElevageForm

def nouveau(request):
    if request.method == 'POST':
        
        form = ElevageForm(request.POST)
        if form.is_valid():
            
            elevage = form.save()
            return redirect('elevage_succes')
        
    else:
        
        form = ElevageForm()

    return render(request, 'elevage/new.html', {'form': form})
