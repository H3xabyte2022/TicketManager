from celery import shared_task
import cloudinary.uploader
from .models import Image

@shared_task
def upload_image_to_cloudinary(image_id):
    image = Image.objects.get(id=image_id)
    response = cloudinary.uploader.upload(image.image_url)
    image.image_url = response['secure_url']
    image.save()
    
    ticket = image.ticket
    if ticket.images.count() == ticket.num_images:
        ticket.status = 'completed'
        ticket.save()