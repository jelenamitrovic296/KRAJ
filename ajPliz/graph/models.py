# graph/models.py
from django.db import models

from django.db import models


class Student(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    ime = models.CharField(max_length=100)
    prezime = models.CharField(max_length=100)
    naslov = models.CharField(max_length=100)
    smer = models.CharField(max_length=100)
    godina_odbrane = models.IntegerField()  # Dodala nova polje za godinu odbrane
    tip_teze = models.CharField(max_length=100)

class Profesor(models.Model):
    ime = models.CharField(max_length=100)
    prezime = models.CharField(max_length=100)
    institucija = models.CharField(max_length=100)

