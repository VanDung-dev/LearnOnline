"""
Tests for Search API endpoints.
"""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from app.courses.models import Category, Course, Module, Lesson


class SearchCoursesAPITestCase(APITestCase):
    """Test cases for course search endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.search_url = reverse('search-courses')

        # Create instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='InstructorPass123!',
            first_name='John',
            last_name='Doe'
        )

        # Create categories
        self.category1 = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.category2 = Category.objects.create(
            name='Design',
            description='Design courses'
        )

        # Create courses
        self.course1 = Course.objects.create(
            title='Python for Beginners',
            slug='python-beginners',
            short_description='Learn Python basics',
            description='A comprehensive Python course',
            instructor=self.instructor,
            category=self.category1,
            price=0,
            is_active=True
        )
        self.course2 = Course.objects.create(
            title='Advanced JavaScript',
            slug='advanced-js',
            short_description='Master JavaScript',
            description='Advanced JS techniques',
            instructor=self.instructor,
            category=self.category1,
            price=99.99,
            is_active=True
        )
        self.course3 = Course.objects.create(
            title='UI/UX Design',
            slug='ui-ux-design',
            short_description='Learn UI/UX fundamentals',
            description='Design beautiful interfaces',
            instructor=self.instructor,
            category=self.category2,
            price=49.99,
            is_active=True
        )

    def test_search_courses_by_title(self):
        """Test searching courses by title."""
        response = self.client.get(self.search_url, {'q': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['title'],
            'Python for Beginners'
        )

    def test_search_courses_by_description(self):
        """Test searching courses by description."""
        response = self.client.get(self.search_url, {'q': 'comprehensive'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_courses_by_instructor(self):
        """Test searching courses by instructor name."""
        response = self.client.get(self.search_url, {'q': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all courses by this instructor
        self.assertEqual(len(response.data['results']), 3)

    def test_search_courses_filter_by_category(self):
        """Test filtering search results by category."""
        response = self.client.get(self.search_url, {
            'q': 'Learn',
            'category': self.category1.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only Python course in category1 matches "Learn"
        for course in response.data['results']:
            self.assertEqual(course['category_name'], 'Programming')

    def test_search_courses_filter_free(self):
        """Test filtering free courses."""
        response = self.client.get(self.search_url, {
            'q': 'Python',
            'is_free': 'true'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for course in response.data['results']:
            self.assertTrue(course['is_free'])

    def test_search_courses_price_range(self):
        """Test filtering by price range."""
        response = self.client.get(self.search_url, {
            'q': 'Learn',
            'min_price': 40,
            'max_price': 60
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for course in response.data['results']:
            self.assertGreaterEqual(float(course['price']), 40)
            self.assertLessEqual(float(course['price']), 60)

    def test_search_requires_minimum_query_length(self):
        """Test that search requires at least 2 characters."""
        response = self.client.get(self.search_url, {'q': 'a'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_ordering_newest(self):
        """Test ordering by newest first."""
        response = self.client.get(self.search_url, {
            'q': 'Python',
            'ordering': 'newest'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SearchLessonsAPITestCase(APITestCase):
    """Test cases for lesson search endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.search_url = reverse('search-lessons')

        # Create instructor and course
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='InstructorPass123!'
        )
        self.category = Category.objects.create(name='Programming')
        self.course = Course.objects.create(
            title='Python Course',
            slug='python-course',
            instructor=self.instructor,
            category=self.category,
            is_active=True
        )
        self.module = Module.objects.create(
            course=self.course,
            title='Getting Started',
            order=1
        )

        # Create lessons
        self.lesson1 = Lesson.objects.create(
            module=self.module,
            title='Introduction to Python',
            slug='intro-python',
            content='Python is a powerful language',
            lesson_type='text',
            is_published=True,
            order=1
        )
        self.lesson2 = Lesson.objects.create(
            module=self.module,
            title='Variables and Data Types',
            slug='variables-data',
            content='Learn about Python variables',
            lesson_type='text',
            is_published=True,
            order=2
        )

    def test_search_lessons_by_title(self):
        """Test searching lessons by title."""
        response = self.client.get(self.search_url, {'q': 'Introduction'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['title'],
            'Introduction to Python'
        )

    def test_search_lessons_by_content(self):
        """Test searching lessons by content."""
        response = self.client.get(self.search_url, {'q': 'powerful'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_lessons_filter_by_course(self):
        """Test filtering lessons by course slug."""
        response = self.client.get(self.search_url, {
            'q': 'Python',
            'course': 'python-course'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AutocompleteAPITestCase(APITestCase):
    """Test cases for autocomplete endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.autocomplete_url = reverse('search-autocomplete')

        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='InstructorPass123!'
        )
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.course = Course.objects.create(
            title='Python Masterclass',
            slug='python-masterclass',
            instructor=self.instructor,
            category=self.category,
            is_active=True
        )

    def test_autocomplete_courses(self):
        """Test autocomplete returns course suggestions."""
        response = self.client.get(self.autocomplete_url, {'q': 'Pyth'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

        # Check first suggestion is the course
        suggestion = response.data[0]
        self.assertEqual(suggestion['type'], 'course')
        self.assertIn('Python', suggestion['text'])

    def test_autocomplete_categories(self):
        """Test autocomplete returns category suggestions."""
        response = self.client.get(self.autocomplete_url, {'q': 'Prog'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should include category suggestion
        types = [s['type'] for s in response.data]
        self.assertIn('category', types)

    def test_autocomplete_limit(self):
        """Test autocomplete respects limit parameter."""
        response = self.client.get(self.autocomplete_url, {
            'q': 'Py',
            'limit': 3
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 3)


class GlobalSearchAPITestCase(APITestCase):
    """Test cases for global search endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.search_url = reverse('search-global')

        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='InstructorPass123!'
        )
        self.category = Category.objects.create(
            name='Python Programming',
            description='Python courses'
        )
        self.course = Course.objects.create(
            title='Python Basics',
            slug='python-basics',
            short_description='Learn Python',
            instructor=self.instructor,
            category=self.category,
            is_active=True
        )

    def test_global_search_returns_all_types(self):
        """Test global search returns courses, lessons, categories."""
        response = self.client.get(self.search_url, {'q': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response structure
        self.assertIn('query', response.data)
        self.assertIn('courses', response.data)
        self.assertIn('lessons', response.data)
        self.assertIn('categories', response.data)

        # Check query is echoed back
        self.assertEqual(response.data['query'], 'Python')

    def test_global_search_finds_courses(self):
        """Test global search includes matching courses."""
        response = self.client.get(self.search_url, {'q': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['courses']), 0)

    def test_global_search_finds_categories(self):
        """Test global search includes matching categories."""
        response = self.client.get(self.search_url, {'q': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['categories']), 0)


class PopularSearchTermsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.url = reverse('search-popular')
        
        # Create some search history
        from app.courses.services.search_service import log_search_query
        log_search_query("python", self.user)
        log_search_query("python", self.user)
        log_search_query("django", self.user)

    def test_get_popular_terms(self):
        """Test retrieving popular search terms"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(len(data) >= 2)
        # Order is not guaranteed to be stable for same count, but python is 2, django is 1
        self.assertEqual(data[0]['query'], 'python')
        self.assertEqual(data[0]['count'], 2)
        self.assertEqual(data[1]['query'], 'django')
        self.assertEqual(data[1]['count'], 1)

    def test_popular_terms_limit(self):
        """Test limit parameter"""
        response = self.client.get(self.url, {'limit': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['query'], 'python')
