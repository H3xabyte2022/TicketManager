from django.urls import path
from .views import TicketCreateView, ImageUploadView, TicketListView, TicketDetailView

urlpatterns = [
    path('tickets/', TicketCreateView.as_view(), name='ticket-create'),
    path('upload-image/', ImageUploadView.as_view(), name='image-upload'),
    path('my-tickets/', TicketListView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
]