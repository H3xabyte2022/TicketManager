from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Ticket, Image

from datetime import datetime, timedelta



class TicketTests(APITestCase):




    def setUp(self):
        # Create a user and obtain a token
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.token = self.client.post(reverse('rest_login'), {'username': 'testuser', 'password': 'testpassword'}).data['key']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)




    def test_create_ticket(self):
        url = reverse('ticket-create')
        data = {'num_images': 3}
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_upload_image(self):
        # First, create a ticket
        ticket = Ticket.objects.create(user=self.user, num_images=3)
        url = reverse('image-upload')
        data = {'ticket': ticket.id, 'image_url': 'https://images-assets.nasa.gov/image/KSC-20240528-PH-CSH01_0088/KSC-20240528-PH-CSH01_0088~medium.jpg'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.get().image_url, 'https://images-assets.nasa.gov/image/KSC-20240528-PH-CSH01_0088/KSC-20240528-PH-CSH01_0088~medium.jpg')




    def test_list_tickets(self):
        # Create a few tickets
        Ticket.objects.create(user=self.user, num_images=3)
        Ticket.objects.create(user=self.user, num_images=5)
        url = reverse('ticket-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)




    def test_ticket_detail(self):
        # Create a ticket
        ticket = Ticket.objects.create(user=self.user, num_images=3)
        url = reverse('ticket-detail', kwargs={'pk': ticket.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num_images'], 3)




    def test_ticket_filter_by_status(self):
        # Create tickets with different statuses
        Ticket.objects.create(user=self.user, num_images=3, status='pending')
        Ticket.objects.create(user=self.user, num_images=3, status='completed')
        url = reverse('ticket-list')
        response = self.client.get(url, {'status': 'pending'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')




    def test_ticket_filter_by_date(self):
     

        # Create tickets with different creation dates
        Ticket.objects.create(user=self.user, num_images=3, created_at=datetime.now() - timedelta(days=2))
        Ticket.objects.create(user=self.user, num_images=3, created_at=datetime.now())
        tickets = Ticket.objects.all()
        print('Created Tickets:', tickets)
        
        url = reverse('ticket-list')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  # Hasta el final del día de mañana
        response = self.client.get(url, {'start_date': start_date, 'end_date': end_date}, format='json')
        
        print('Response Data:', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


    def test_no_update_ticket(self):
        ticket = Ticket.objects.create(user=self.user, num_images=3)
        url = reverse('ticket-detail', kwargs={'pk': ticket.id})
        data = {'num_images': 5}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)




    def test_no_delete_ticket(self):
        ticket = Ticket.objects.create(user=self.user, num_images=3)
        url = reverse('ticket-detail', kwargs={'pk': ticket.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)




class ImageTests(APITestCase):



    def setUp(self):
        # Create a user and obtain a token
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.token = self.client.post(reverse('rest_login'), {'username': 'testuser', 'password': 'testpassword'}).data['key']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.ticket = Ticket.objects.create(user=self.user, num_images=3)



    def test_upload_image(self):
        url = reverse('image-upload')
        data = {'ticket': self.ticket.id, 'image_url': 'https://images-assets.nasa.gov/image/iss071e092797/iss071e092797~medium.jpg'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.get().image_url, 'https://images-assets.nasa.gov/image/iss071e092797/iss071e092797~medium.jpg')



    def test_no_upload_image_exceed_limit(self):
        for _ in range(3):
            Image.objects.create(ticket=self.ticket, image_url='https://images-assets.nasa.gov/image/jsc2024e036350/jsc2024e036350~medium.jpg')
        url = reverse('image-upload')
        data = {'ticket': self.ticket.id, 'image_url': 'https://images-assets.nasa.gov/image/KSC-20240525-PH-RKL01_0006/KSC-20240525-PH-RKL01_0006~medium.jpg'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)