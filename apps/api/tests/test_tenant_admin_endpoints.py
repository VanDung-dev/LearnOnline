import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.organization.models import School
from apps.courses.models import Category, Course, Enrollment


@pytest.mark.django_db
class TestTenantAdminEndpoints:
    def setup_method(self):
        self.client = APIClient()

        # Schools
        self.school_a = School.objects.create(name="Đại học A", code="uni_a", domain="unia.edu.vn")
        self.school_b = School.objects.create(name="Cao đẳng B", code="col_b", domain="colb.edu.vn")

        # Users
        self.admin_a = User.objects.create_user(username="admin_a", password="pass")
        admin_a_profile = self.admin_a.profile
        admin_a_profile.role = Profile.SCHOOL_ADMIN
        admin_a_profile.school = self.school_a
        admin_a_profile.save()

        self.admin_b = User.objects.create_user(username="admin_b", password="pass")
        admin_b_profile = self.admin_b.profile
        admin_b_profile.role = Profile.SCHOOL_ADMIN
        admin_b_profile.school = self.school_b
        admin_b_profile.save()

        self.instructor_a = User.objects.create_user(username="instructor_a", password="pass")
        instructor_a_profile = self.instructor_a.profile
        instructor_a_profile.role = Profile.INSTRUCTOR
        instructor_a_profile.school = self.school_a
        instructor_a_profile.save()

        self.instructor_b = User.objects.create_user(username="instructor_b", password="pass")
        instructor_b_profile = self.instructor_b.profile
        instructor_b_profile.role = Profile.INSTRUCTOR
        instructor_b_profile.school = self.school_b
        instructor_b_profile.save()

        self.student_1 = User.objects.create_user(username="student_1", password="pass")
        self.student_1.profile.role = Profile.STUDENT
        self.student_1.profile.save()

        self.student_2 = User.objects.create_user(username="student_2", password="pass")
        self.student_2.profile.role = Profile.STUDENT
        self.student_2.profile.save()

        # Catalog
        self.cat = Category.objects.create(name="Data Science")

        # Courses
        self.course_a = Course.objects.create(
            title="ML A",
            slug="ml-a",
            category=self.cat,
            instructor=self.instructor_a,
            price=0,
        )
        self.course_b = Course.objects.create(
            title="React B",
            slug="react-b",
            category=self.cat,
            instructor=self.instructor_b,
            price=0,
        )

        # Enrollments
        Enrollment.objects.create(user=self.student_1, course=self.course_a)
        Enrollment.objects.create(user=self.student_2, course=self.course_b)

    def test_admin_courses_filtered_by_school(self):
        self.client.force_authenticate(self.admin_a)
        url = f"/api/schools/{self.school_a.id}/admin/courses/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        if isinstance(data, dict) and "results" in data:
            data = data["results"]
        slugs = [c["slug"] for c in data]
        assert "ml-a" in slugs
        assert "react-b" not in slugs

    def test_cross_tenant_access_forbidden(self):
        self.client.force_authenticate(self.admin_a)
        url = f"/api/schools/{self.school_b.id}/admin/courses/"
        resp = self.client.get(url)
        assert resp.status_code == 403

    def test_admin_students_includes_enrolled_students(self):
        self.client.force_authenticate(self.admin_a)
        url = f"/api/schools/{self.school_a.id}/admin/students/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        if isinstance(data, dict) and "results" in data:
            data = data["results"]
        usernames = [p["user"]["username"] for p in data]
        # student_1 is enrolled in a course of school A → must appear
        assert "student_1" in usernames
        # student_2 only enrolled in school B → must not appear
        assert "student_2" not in usernames
