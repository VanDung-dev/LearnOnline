from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.courses.models import Course, Category
from .models import Discussion, Reply, Vote

class DiscussionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', description='Test Description')
        self.instructor = User.objects.create_user(username='instructor', password='password')
        self.student = User.objects.create_user(username='student', password='password')
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test Description',
            category=self.category,
            instructor=self.instructor
        )
        self.client = APIClient()

    def test_create_discussion_api(self):
        self.client.force_authenticate(user=self.student)
        # Not enrolled yet
        data = {'title': 'Question?', 'body': 'Help', 'course_slug': self.course.slug}
        response = self.client.post('/api/discussions/', data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Enroll (mock or manually create enrollment if needed, but here simple Check is fine)
        # Actually Enrollment logic is complex, let's just create Enrollment model manually
        from apps.courses.models import Enrollment
        Enrollment.objects.create(user=self.student, course=self.course)
        
        response = self.client.post('/api/discussions/', data)
        with open(r'c:\Users\VanDungDev\Documents\GitHub\LearnOnline\debug_test.log', 'a') as f:
            f.write(f"Response 2 status: {response.status_code}\n")
            f.write(f"Response 2 data: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Discussion.objects.count(), 1)

    def test_reply_workflow(self):
        from apps.courses.models import Enrollment
        Enrollment.objects.create(user=self.student, course=self.course)
        
        discussion = Discussion.objects.create(
            course=self.course, author=self.student, title='Help', body='Me'
        )
        
        self.client.force_authenticate(user=self.instructor)
        data = {'body': 'Answer'}
        url = f'/api/discussions/{discussion.id}/reply/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(discussion.replies.count(), 1)
        
        reply_id = response.data['id']
        
        # Vote on reply
        vote_url = f'/api/replies/{reply_id}/vote/'
        self.client.post(vote_url, {'vote_type': 1})
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote_type, 1)

    def test_mark_answer_permission(self):
        from apps.courses.models import Enrollment
        Enrollment.objects.create(user=self.student, course=self.course)
        
        discussion = Discussion.objects.create(
            course=self.course, author=self.student, title='Help', body='Me'
        )
        reply = Reply.objects.create(discussion=discussion, author=self.instructor, body='Ans')
        
        # Random user cannot mark
        other_user = User.objects.create_user(username='other', password='password')
        self.client.force_authenticate(user=other_user)
        url = f'/api/replies/{reply.id}/mark_answer/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Author can mark
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reply.refresh_from_db()
        self.assertTrue(reply.is_answer)
