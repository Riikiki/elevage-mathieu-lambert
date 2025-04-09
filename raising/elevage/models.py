from django.db import models

# Create your models here.

class rabbit(models.Model):
    genre = models.IntegerField()
    
class cage(models.Model):
    nbRabbit = models.ForeignKey(rabbit, on_delete=models.CASCADE)
    
class cash(models.Model):
    funds = models.FloatField(default=0.0)
    
class elevage(models.Model):
    nbCage = models.ForeignKey(cage, on_delete=models.CASCADE)
    
class player(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    inGameRaising = models.IntegerField(default=0)
    
    def __str__(self):
        return self.username