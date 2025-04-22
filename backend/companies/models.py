# backend/companies/models.py
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=50)
    subscription_end = models.DateField()

    def __str__(self):
        return self.name