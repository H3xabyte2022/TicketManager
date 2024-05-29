from django.contrib import admin
from .models import Ticket, Image





@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'num_images', 'status', 'created_at', 'updated_at')
    readonly_fields = ('user', 'num_images', 'status', 'created_at', 'updated_at')





@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'image_url', 'uploaded_at')
    readonly_fields = ('ticket', 'image_url', 'uploaded_at')