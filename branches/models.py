from django.db import models
from places.models import Place


class Branch(models.Model):
    organization = models.ForeignKey(Place, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    schedule = models.JSONField(default=dict)
