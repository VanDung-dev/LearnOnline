from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile


class ProfileModelTest(TestCase):
    def setUp(self):
        # Create test users
        self.student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123'
        )
        self.student_user.profile.role = Profile.STUDENT
        self.student_user.profile.save()
        self.student_profile = self.student_user.profile
        
        self.instructor_user = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123'
        )
        self.instructor_user.profile.role = Profile.INSTRUCTOR
        self.instructor_user.profile.save()
        self.instructor_profile = self.instructor_user.profile
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.profile.role = Profile.ADMIN
        self.admin_user.profile.save()
        self.admin_profile = self.admin_user.profile

    def test_profile_roles(self):
        # Test student role
        self.assertTrue(self.student_profile.is_student())
        self.assertFalse(self.student_profile.is_instructor())
        self.assertFalse(self.student_profile.is_admin())
        
        # Test instructor role
        self.assertTrue(self.instructor_profile.is_instructor())
        self.assertFalse(self.instructor_profile.is_student())
        self.assertFalse(self.instructor_profile.is_admin())
        
        # Test admin role
        self.assertTrue(self.admin_profile.is_admin())
        self.assertFalse(self.admin_profile.is_student())
        self.assertFalse(self.admin_profile.is_instructor())

    def test_custom_user_manager(self):
        # Test custom managers
        students = User.objects.students()
        instructors = User.objects.instructors()
        admins = User.objects.admins()
        
        self.assertEqual(students.count(), 1)
        self.assertEqual(instructors.count(), 1)
        self.assertEqual(admins.count(), 1)
        
        self.assertIn(self.instructor_user, instructors)
        self.assertIn(self.admin_user, admins)


class StudentDashboardTest(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username='student_dash',
            email='student_dash@test.com',
            password='testpass123'
        )
        self.student_user.profile.role = Profile.STUDENT
        self.student_user.profile.save()
        
        # Create course and enrollment
        from apps.courses.models import Course, Category, Enrollment
        self.category = Category.objects.create(name='Test Category')
        self.instructor = User.objects.create_user(username='inst', password='pw')
        self.course = Course.objects.create(
            title='Test Course',
            category=self.category,
            instructor=self.instructor,
            price=100
        )
        self.enrollment = Enrollment.objects.create(
            user=self.student_user,
            course=self.course
        )
        
        # Create payment
        from apps.payments.models import Payment
        self.payment = Payment.objects.create(
            user=self.student_user,
            course=self.course,
            amount=100,
            transaction_id='TRANS123',
            payment_method='visa',
            status='completed'
        )

    def test_dashboard_view(self):
        self.client.login(username='student_dash', password='testpass123')
        # Use the new global dashboard URL
        response = self.client.get(reverse('user_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_dashboard.html')
        
        # Check context
        self.assertIn('enrollments', response.context)
        self.assertIn('payments', response.context)
        self.assertEqual(len(response.context['enrollments']), 1)
        self.assertEqual(len(response.context['payments']), 1)
        
        # Check content
        self.assertNotContains(response, 'Purchased Courses')
        self.assertContains(response, 'Payment History')
        self.assertContains(response, 'TRANS123')
        self.assertContains(response, 'Test Course')

    def test_student_dashboard_url(self):
        """
        Test that the old student dashboard URL redirects to the new profile dashboard.
        """
        self.client.login(username='student_dash', password='testpass123')
        response = self.client.get(reverse('courses:student_dashboard'))
        
        # Expect redirect to user_dashboard
        self.assertRedirects(response, reverse('user_dashboard'))
        
        # Follow redirect to verify content
        response = self.client.get(reverse('courses:student_dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_dashboard.html')
        self.assertContains(response, 'Test Course')


class InstructorProfileTest(TestCase):
    def setUp(self):
        from apps.accounts.models import Profile
        self.instructor = User.objects.create_user(
            username='inst_prof',
            email='inst_prof@example.com',
            password='testpass123'
        )
        if hasattr(self.instructor, 'profile'):
            self.instructor.profile.role = Profile.INSTRUCTOR
            self.instructor.profile.save()
        else:
            Profile.objects.create(user=self.instructor, role=Profile.INSTRUCTOR)
        
        self.student = User.objects.create_user(
            username='student_prof',
            email='student@example.com',
            password='testpass123'
        )
        
        from apps.courses.models import Category, Course, Enrollment
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Instructor Course',
            category=self.category,
            instructor=self.instructor,
            price=50
        )
        
        self.enrollment = Enrollment.objects.create(
            user=self.student,
            course=self.course
        )

    def test_profile_view_enrollments(self):
        self.client.login(username='inst_prof', password='testpass123')
        from django.urls import reverse_lazy
        response = self.client.get(reverse_lazy('user_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_dashboard.html')
        
        # Check context
        self.assertIn('enrollments', response.context)
        self.assertIn('courses', response.context)
        self.assertEqual(len(response.context['enrollments']), 1)
        self.assertEqual(response.context['enrollments'][0], self.enrollment)
        
        # Check content
        self.assertContains(response, 'Recent Enrollments')
        self.assertContains(response, 'student_prof')
