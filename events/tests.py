from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Event, RSVP, Review, UserProfile
from datetime import datetime, timedelta
from django.utils import timezone


class EventAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123'
        )
        
        # Create user profiles
        UserProfile.objects.create(
            user=self.user,
            full_name='Test User',
            bio='Test bio'
        )
        UserProfile.objects.create(
            user=self.organizer,
            full_name='Event Organizer',
            bio='Organizer bio'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            organizer=self.organizer,
            location='Test Location',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            is_public=True
        )
    
    def test_create_event_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Event',
            'description': 'New Description',
            'location': 'New Location',
            'start_time': (timezone.now() + timedelta(days=2)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=2, hours=2)).isoformat(),
            'is_public': True
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['organizer']['id'], self.user.id)
    
    def test_create_event_unauthenticated(self):
        data = {
            'title': 'New Event',
            'description': 'New Description',
            'location': 'New Location',
            'start_time': (timezone.now() + timedelta(days=2)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=2, hours=2)).isoformat(),
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_public_events(self):
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_rsvp_to_event(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/events/{self.event.id}/rsvp/', {'status': 'Going'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Going')
    
    def test_add_review(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/events/{self.event.id}/reviews/',
            {'rating': 5, 'comment': 'Great event!'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
    
    def test_update_event_by_organizer(self):
        self.client.force_authenticate(user=self.organizer)
        response = self.client.patch(
            f'/api/events/{self.event.id}/',
            {'title': 'Updated Event Title'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Event Title')
    
    def test_update_event_by_non_organizer(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/events/{self.event.id}/',
            {'title': 'Updated Event Title'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
