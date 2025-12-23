"""
Tests for API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from app.courses.models import Category, Course


class AuthAPITestCase(APITestCase):
    """Test cases for authentication endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.register_url = reverse('api-register')
        self.login_url = reverse('api-token-obtain')

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration(self):
        """Test user registration endpoint."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_password_mismatch(self):
        """Test registration fails with password mismatch."""
        data = self.user_data.copy()
        data['password2'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login endpoint."""
        # Create user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

        # Login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class CourseAPITestCase(APITestCase):
    """Test cases for course endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create instructor user
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='InstructorPass123!'
        )

        # Create category
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )

        # Create course
        self.course = Course.objects.create(
            title='Python Basics',
            slug='python-basics',
            description='Learn Python programming',
            instructor=self.instructor,
            category=self.category,
            is_free=True
        )

    def test_list_courses(self):
        """Test listing courses."""
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_course_detail(self):
        """Test getting course detail."""
        url = reverse('course-detail', kwargs={'slug': 'python-basics'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Basics')

    def test_filter_courses_by_category(self):
        """Test filtering courses by category."""
        url = reverse('course-list') + f'?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_free_courses(self):
        """Test filtering free courses."""
        url = reverse('course-list') + '?is_free=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class EnrollmentAPITestCase(APITestCase):
    """Test cases for enrollment endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create users
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StudentPass123!'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='InstructorPass123!'
        )

        # Create category and course
        self.category = Category.objects.create(name='Web Dev')
        self.course = Course.objects.create(
            title='Django Mastery',
            slug='django-mastery',
            description='Master Django',
            instructor=self.instructor,
            category=self.category,
            is_free=True
        )

    def test_enroll_authenticated_user(self):
        """Test enrollment for authenticated user."""
        self.client.force_authenticate(user=self.student)
        url = reverse('course-enroll', kwargs={'slug': 'django-mastery'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_enroll_unauthenticated_user(self):
        """Test enrollment fails for unauthenticated user."""
        url = reverse('course-enroll', kwargs={'slug': 'django-mastery'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_double_enrollment_fails(self):
        """Test user cannot enroll twice."""
        self.client.force_authenticate(user=self.student)
        url = reverse('course-enroll', kwargs={'slug': 'django-mastery'})

        # First enrollment
        self.client.post(url)

        # Second enrollment should fail
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CategoryAPITestCase(APITestCase):
    """Test cases for category endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        Category.objects.create(name='Category 1')
        Category.objects.create(name='Category 2')

    def test_list_categories(self):
        """Test listing categories."""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
