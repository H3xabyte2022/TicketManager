from rest_framework import serializers
from ..models import Ticket, Image



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'




class TicketSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'