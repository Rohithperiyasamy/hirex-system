from django.db import models

# Create your models here.


class Feedback(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    feedback = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)  # Rating from 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set to current date and time when created