from django.db import models
from django.contrib.auth.models import User



"""This is the main ticket model"""
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    num_images = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



"""This is an image model used for tracking Image information"""
class Image(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)