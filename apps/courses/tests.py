from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Category, Course, Enrollment, Certificate, Progress, Lesson, Section


class CourseExpirationTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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
        
        # Create course with expiration date
        self.expiring_course = Course.objects.create(
            title='Test Course with Expiration',
            description='Test course description',
            category=self.category,
            instructor=self.instructor,
            price=100.00,
            expiration_date=timezone.now() + timedelta(days=30)  # Expires in 30 days
        )
        
        # Create course without expiration date
        self.non_expiring_course = Course.objects.create(
            title='Test Course without Expiration',
            description='Test course description',
            category=self.category,
            instructor=self.instructor,
            price=100.00
        )
        
        # Create section and lesson for the course
        self.section = Section.objects.create(
            course=self.expiring_course,
            title='Test Section',
            description='Test section description',
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            section=self.section,
            title='Test Lesson',
            lesson_type='text',
            content='Test lesson content',
            order=1
        )

    def test_course_expiration_date_field(self):
        """Test that expiration date field works correctly"""
        self.assertIsNotNone(self.expiring_course.expiration_date)
        self.assertIsNone(self.non_expiring_course.expiration_date)
        
    def test_certificate_issued_before_expiration(self):
        """Test that certificate is issued when course is completed before expiration"""
        # Create enrollment for the expiring course
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.expiring_course
        )
        
        # Mark lesson as completed
        progress = Progress.objects.create(
            user=self.user,
            lesson=self.lesson,
            completed=True
        )
        
        # Simulate checking for certificate issuance
        from apps.courses.views import check_and_issue_certificate
        check_and_issue_certificate(self.user, self.expiring_course)
        
        # Check that certificate was issued
        certificate_exists = Certificate.objects.filter(
            user=self.user,
            course=self.expiring_course
        ).exists()
        self.assertTrue(certificate_exists)
        
    def test_certificate_not_issued_after_expiration(self):
        """Test that certificate is not issued when course expires"""
        # Create an expired course
        expired_course = Course.objects.create(
            title='Expired Test Course',
            description='Expired test course description',
            category=self.category,
            instructor=self.instructor,
            price=100.00,
            expiration_date=timezone.now() - timedelta(days=1)  # Expired yesterday
        )
        
        # Create section and lesson for the expired course
        section = Section.objects.create(
            course=expired_course,
            title='Test Section',
            description='Test section description',
            order=1
        )
        
        lesson = Lesson.objects.create(
            section=section,
            title='Test Lesson',
            lesson_type='text',
            content='Test lesson content',
            order=1
        )
        
        # Create enrollment for the expired course
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=expired_course
        )
        
        # Mark lesson as completed
        progress = Progress.objects.create(
            user=self.user,
            lesson=lesson,
            completed=True
        )
        
        # Simulate checking for certificate issuance
        from apps.courses.views import check_and_issue_certificate
        check_and_issue_certificate(self.user, expired_course)
        
        # Check that certificate was NOT issued
        certificate_exists = Certificate.objects.filter(
            user=self.user,
            course=expired_course
        ).exists()
        self.assertFalse(certificate_exists)


class CourseScheduleTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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
        
        # Create a course with opening and closing dates
        now = timezone.now()
        self.scheduled_course = Course.objects.create(
            title='Scheduled Test Course',
            description='Scheduled test course description',
            category=self.category,
            instructor=self.instructor,
            price=100.00,
            opening_date=now + timedelta(days=1),  # Opens tomorrow
            closing_date=now + timedelta(days=30)  # Closes in 30 days
        )

    def test_course_opening_date(self):
        """Test that course with future opening date is not accessible"""
        # This test would require making a request to the course detail view
        # and checking that it raises Http404
        pass
        
    def test_course_closing_date(self):
        """Test that course with past closing date is not accessible"""
        # This test would require making a request to the course detail view
        # and checking that it raises Http404
        pass