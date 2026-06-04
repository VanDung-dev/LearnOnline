from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.courses.models import Category, Course, Enrollment, Certificate, Progress, Lesson, Section, Subsection


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
        
        # Create section, subsection and lesson for the course
        self.section = Section.objects.create(
            course=self.expiring_course,
            title='Test Section',
            description='Test section description',
            order=1
        )
        
        self.subsection = Subsection.objects.create(
            section=self.section,
            title='Test Subsection',
            description='Test subsection description',
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            subsection=self.subsection,
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
        cert = Certificate.objects.filter(
            user=self.user,
            course=self.expiring_course
        ).first()
        self.assertIsNotNone(cert)
        
        # Print status for debugging
        print(f"\n--- CERTIFICATE HIERACHAIN STATUS: {cert.blockchain_status} ---")
        print(f"TX Hash: {cert.blockchain_tx_hash}")
        print(f"Block: {cert.blockchain_block_number}")
        print(f"Crypto Hash: {cert.cryptographic_hash}")
        
        self.assertEqual(cert.blockchain_status, 'synced')
        self.assertIsNotNone(cert.blockchain_tx_hash)
        self.assertIsNotNone(cert.cryptographic_hash)
        
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
        
        # Create section, subsection and lesson for the expired course
        section = Section.objects.create(
            course=expired_course,
            title='Test Section',
            description='Test section description',
            order=1
        )
        
        subsection = Subsection.objects.create(
            section=section,
            title='Test Subsection',
            description='Test subsection description',
            order=1
        )
        
        lesson = Lesson.objects.create(
            subsection=subsection,
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

    def test_hierachain_readiness_schema(self):
        """Test that HieraChain readiness fields exist on Certificate and save successfully"""
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.expiring_course
        )
        certificate = Certificate.objects.create(
            user=self.user,
            course=self.expiring_course,
            enrollment=enrollment,
            blockchain_tx_hash="0x" + "a" * 64,
            blockchain_block_number=1000,
            blockchain_status='synced',
            cryptographic_hash="b" * 64
        )
        self.assertEqual(certificate.blockchain_tx_hash, "0x" + "a" * 64)
        self.assertEqual(certificate.blockchain_block_number, 1000)
        self.assertEqual(certificate.blockchain_status, 'synced')
        self.assertEqual(certificate.cryptographic_hash, "b" * 64)

    def test_can_generate_certificate_service_logic(self):
        """Test that can_generate_certificate service counts lessons, not sections"""
        from apps.courses.services.certificate_service import can_generate_certificate
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.expiring_course
        )
        
        # Initially, not eligible as lesson is not completed
        self.assertFalse(can_generate_certificate(self.user, self.expiring_course))
        
        # Mark lesson completed
        progress = Progress.objects.create(
            user=self.user,
            lesson=self.lesson,
            completed=True
        )
        
        # Eligible now that all lessons (1/1) in course are completed
        self.assertTrue(can_generate_certificate(self.user, self.expiring_course))


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
