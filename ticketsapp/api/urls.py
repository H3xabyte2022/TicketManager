from django.urls import path
from .views import TicketCreateView, ImageUploadView, TicketListView, TicketDetailView

urlpatterns = [
    path('tickets/', TicketCreateView.as_view(), name='ticket-create'),
    path('upload-image/', ImageUploadView.as_view(), name='image-upload'),
    
]