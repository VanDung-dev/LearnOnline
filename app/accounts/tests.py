from django.test import TestCase
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
        
        self.assertIn(self.student_user, students)
        self.assertIn(self.instructor_user, instructors)
        self.assertIn(self.admin_user, admins)