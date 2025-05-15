from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sector = models.CharField(max_length=50)
    subscription_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name