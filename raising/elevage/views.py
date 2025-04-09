from django.shortcuts import render
from elevage.models import elevage

# Create your views here.

def new(request):
    if request.method == 'POST':
        nbRabbit = request.POST.get('nbRabbit')
        nbCage = request.POST.get('nbCage')
        funds = request.POST.get('funds')
        foodQuantity = request.POST.get('foodQuantity')
        username = request.POST.get('username')

        elevage_instance = elevage(
            nbRabbit=nbRabbit,
            nbCage=nbCage,
            funds=funds,
            foodQuantity=foodQuantity,
            username=username
        )
        elevage_instance.save()
    return render(request, 'elevage/new.html')