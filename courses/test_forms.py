from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .forms import CourseForm
from .models import Category, User


class CourseFormTestCase(TestCase):
    def setUp(self):
        # Create instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123'
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )

    def test_course_form_with_date_fields(self):
        """Test that course form accepts date fields"""
        now = timezone.now()
        future_date = now + timedelta(days=30)
        past_date = now - timedelta(days=10)
        
        form_data = {
            'title': 'Test Course with Dates',
            'short_description': 'A short description',
            'description': 'A full description',
            'category': self.category.id,
            'price': 99.99,
            'is_active': True,
            'opening_date': now.strftime('%Y-%m-%dT%H:%M'),
            'closing_date': future_date.strftime('%Y-%m-%dT%H:%M'),
            'expiration_date': future_date.strftime('%Y-%m-%dT%H:%M'),
        }
        
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Save the form
        course = form.save(commit=False)
        course.instructor = self.instructor
        course.save()
        
        # Check that the dates were saved correctly
        self.assertIsNotNone(course.opening_date)
        self.assertIsNotNone(course.closing_date)
        self.assertIsNotNone(course.expiration_date)
        
    def test_course_form_without_date_fields(self):
        """Test that course form works without date fields (for backward compatibility)"""
        form_data = {
            'title': 'Test Course without Dates',
            'short_description': 'A short description',
            'description': 'A full description',
            'category': self.category.id,
            'price': 99.99,
            'is_active': True,
        }
        
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Save the form
        course = form.save(commit=False)
        course.instructor = self.instructor
        course.save()
        
        # Check that the dates are None
        self.assertIsNone(course.opening_date)
        self.assertIsNone(course.closing_date)
        self.assertIsNone(course.expiration_date)