from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Notification

User = get_user_model()

class NotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.notification = Notification.objects.create(
            recipient=self.user,
            title="Test Notification",
            message="Test Message",
            notification_type="system"
        )

    def test_get_notifications(self):
        url = reverse('notifications:api_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Test Notification")

    def test_unread_count(self):
        url = reverse('notifications:api_unread_count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_mark_read(self):
        url = reverse('notifications:api_mark_read', kwargs={'pk': self.notification.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
