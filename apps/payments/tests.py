from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from apps.courses.models import Category, Course


class PaymentFlowTests(TestCase):
    def setUp(self):
        # User and login
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.client.login(username="buyer", password="pass12345")

        # Minimal course setup
        self.category = Category.objects.create(name="Cat", description="D")
        self.course = Course.objects.create(
            title="Sample Course",
            slug="sample-course",
            short_description="Short",
            description="Desc",
            category=self.category,
            instructor=self.user,
            price=Decimal("10.00"),
            certificate_price=Decimal("0.00"),
            created_at=timezone.now(),
        )

    def test_process_payment_returns_field_errors_when_missing_params(self):
        url = reverse("payments:process_payment", kwargs={"course_slug": self.course.slug})
        # Missing card_type
        resp = self.client.post(url, {
            "card_number": "4242424242424242",
            "expiry_date": "12/30",
            "cvv": "123",
            # "card_type": "visa"  # intentionally missing
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("success", data)
        self.assertFalse(data["success"])  # standardized schema
        self.assertIn("errors", data)
        # Expect card_type error present
        self.assertIn("card_type", data["errors"]) 

    def test_process_payment_success_returns_transaction_and_redirect(self):
        url = reverse("payments:process_payment", kwargs={"course_slug": self.course.slug})
        resp = self.client.post(url, {
            "card_number": "4242424242424242",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "visa",
            "purchase_type": "course",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertIsNotNone(data.get("transaction_id"))
        self.assertIsNotNone(data.get("redirect_url"))

        # Success page should render for owner
        success_url = data["redirect_url"]
        resp2 = self.client.get(success_url)
        self.assertEqual(resp2.status_code, 200)
        self.assertContains(resp2, self.course.title)
        self.assertContains(resp2, data["transaction_id"]) 
