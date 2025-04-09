from django.db import models
from django.urls import reverse

# Create your models here.

class elevage(models.Model):
    
    nbRabbit = models.IntegerField(default=0)
    nbCage = models.IntegerField(default=0)
    funds = models.FloatField(default=0.0)
    foodQuantity = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})

class player(models.Model):
    
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    
    inGameRaising = models.ForeignKey(elevage, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    
    