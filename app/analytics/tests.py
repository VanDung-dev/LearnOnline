from django.test import TestCase
from django.contrib.auth.models import User
from app.courses.models import Course, Enrollment, Module, Lesson, Progress, Category
from app.analytics.services import get_student_progress, get_instructor_stats

class AnalyticsServiceTests(TestCase):
    def setUp(self):
        # Create Users
        self.instructor = User.objects.create_user(username='instructor', password='password')
        self.student = User.objects.create_user(username='student', password='password')
        
        # Create Category
        self.category = Category.objects.create(name="Test Category")

        # Create Course
        self.course = Course.objects.create(
            title="Test Course", 
            instructor=self.instructor,
            category=self.category,
            price=10.00
        )

        # Create Content
        self.module = Module.objects.create(course=self.course, title="Module 1")
        self.lesson1 = Lesson.objects.create(module=self.module, title="Lesson 1", order=1)
        self.lesson2 = Lesson.objects.create(module=self.module, title="Lesson 2", order=2)

        # Enroll Student
        self.enrollment = Enrollment.objects.create(user=self.student, course=self.course)

    def test_student_progress_zero(self):
        data = get_student_progress(self.student)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['progress_percent'], 0)
        self.assertEqual(data[0]['total_lessons'], 2)
        self.assertEqual(data[0]['completed_lessons'], 0)

    def test_student_progress_partial(self):
        # Complete 1 lesson
        Progress.objects.create(user=self.student, lesson=self.lesson1, completed=True)
        
        data = get_student_progress(self.student)
        self.assertEqual(data[0]['progress_percent'], 50)
        self.assertEqual(data[0]['completed_lessons'], 1)

    def test_instructor_stats(self):
        stats = get_instructor_stats(self.instructor)
        self.assertEqual(stats['total_students'], 1)
        self.assertEqual(stats['total_courses'], 1)
        # Revenue might be 0 as we didn't create Payment records, which is expected
        self.assertEqual(stats['total_revenue'], 0)

