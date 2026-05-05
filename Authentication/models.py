from django.db import models

# Create your models here.
class Interviewee(models.Model):
    name = models.CharField(max_length=15, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    email = models.CharField(max_length=15, blank=True)
    password = models.TextField(blank=False)

class Hr(models.Model):
    name = models.CharField(max_length=15, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    email = models.CharField(max_length=15, blank=True)
    password = models.TextField(blank=False)
    company = models.CharField(max_length=20, blank=True)

    # def __str__(self):
    #     return self.user.username
