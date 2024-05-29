from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Ticket, Image
from .serializers import TicketSerializer, ImageSerializer
from ..tasks import upload_image_to_cloudinary
from django.core.exceptions import PermissionDenied
from rest_framework import mixins
from datetime import datetime

#Added mixins to ensure only permitted operations


class TicketCreateView(generics.CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Obtener el usuario autenticado del token
        user = request.user
        
        # Asignar el usuario al ticket durante la creación
        data = request.data.copy()
        data['user'] = user.id
        
        serializer = TicketSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ImageUploadView(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        ticket = Ticket.objects.get(id=request.data['ticket'])
        if ticket.user != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        if ticket.images.count() >= ticket.num_images:
            return Response({'error': 'Image limit reached'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        upload_image_to_cloudinary.delay(serializer.data['id'])

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




class TicketListView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        print(f"Status: {status}, Start Date: {start_date}, End Date: {end_date}")

        if status:
            queryset = queryset.filter(status=status)
        if start_date and end_date:
            # Convert string dates to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__range=[start_date, end_date])
        
        print("Filtered Queryset:", queryset)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TicketDetailView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        ticket = super().get_object()
        if ticket.user != self.request.user:
            raise PermissionDenied('You do not have permission to view this ticket')
        return ticket

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)