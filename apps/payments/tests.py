from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.conf import settings

from apps.courses.models import Category, Course
from apps.payments.models import Payment


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
        # Missing payment_method
        resp = self.client.post(url, {
            "card_number": "4242424242424242",
            "expiry_date": "12/30",
            "cvv": "123",
            # "payment_method": "visa"  # intentionally missing
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("success", data)
        self.assertFalse(data["success"])  # standardized schema
        self.assertIn("errors", data)
        # Expect payment_method error present
        self.assertIn("payment_method", data["errors"]) 

    def test_process_payment_success_returns_transaction_and_redirect(self):
        url = reverse("payments:process_payment", kwargs={"course_slug": self.course.slug})
        resp = self.client.post(url, {
            "card_number": "4242424242424242",
            "cardholder_name": "JOHN DOE",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "visa",
            "purchase_type": "course",
            "billing_address": "123 Main St",
            "zip_code": "10000",
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

    def test_idempotency_same_token_returns_same_completed_payment(self):
        url = reverse("payments:process_payment", kwargs={"course_slug": self.course.slug})
        token = "token-1234"

        payload = {
            "card_number": "4242424242424242",
            "cardholder_name": "JOHN DOE",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "visa",
            "purchase_type": "course",
            "client_token": token,
            "billing_address": "123 Main St",
            "zip_code": "10000",
        }
        resp1 = self.client.post(url, data=payload)
        self.assertEqual(resp1.status_code, 200)
        d1 = resp1.json()
        self.assertTrue(d1.get("success"))
        self.assertIsNotNone(d1.get("transaction_id"))

        # Second POST with the same token should detect existing payment and return success
        resp2 = self.client.post(url, data=payload)
        self.assertEqual(resp2.status_code, 200)
        d2 = resp2.json()
        self.assertTrue(d2.get("success"))
        self.assertEqual(d1.get("transaction_id"), d2.get("transaction_id"))

    def test_webhook_mock_updates_payment_status(self):
        # Create a pending payment with a known processor_transaction_id
        processor_id = "MOCK-UNITTEST-ABC123"
        pay = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=Decimal("10.00"),
            currency="USD",
            status="pending",
            payment_method="visa",
            purchase_type="course",
            transaction_id="TX-UNIT-0001",
            processor_transaction_id=processor_id,
        )

        webhook_url = reverse("payments:payment_webhook", kwargs={"provider": "mock"})
        # Send a mock webhook signaling completion
        resp = self.client.post(
            webhook_url,
            data={
                "processor_transaction_id": processor_id,
                "status": "completed",
            },
            content_type="application/json",
            **{"HTTP_X_PAYMENTS_SIGNATURE": getattr(settings, "PAYMENTS_WEBHOOK_SECRET", "dev_secret")},
        )
        self.assertEqual(resp.status_code, 200)
        pay.refresh_from_db()
        self.assertEqual(pay.status, "completed")


    def test_process_payment_uses_custom_email(self):
        url = reverse("payments:process_payment", kwargs={"course_slug": self.course.slug})
        resp = self.client.post(url, {
            "card_number": "4242424242424242",
            "cardholder_name": "JOHN DOE",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "visa",
            "purchase_type": "course",
            "billing_address": "123 Main St",
            "zip_code": "10000",
            "email": "custom@example.com",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))


class CardValidationTests(TestCase):
    """Test cases for card number validation (BIN and Luhn)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="cardtest", password="pass12345"
        )
        self.client.login(username="cardtest", password="pass12345")
        self.category = Category.objects.create(name="Cat2", description="D")
        self.course = Course.objects.create(
            title="Validation Course",
            slug="validation-course",
            short_description="Short",
            description="Desc",
            category=self.category,
            instructor=self.user,
            price=Decimal("10.00"),
            certificate_price=Decimal("0.00"),
            created_at=timezone.now(),
        )
        self.url = reverse(
            "payments:process_payment",
            kwargs={"course_slug": self.course.slug}
        )

    def test_visa_card_with_valid_bin_succeeds(self):
        """Visa cards starting with 4 should pass BIN validation."""
        resp = self.client.post(self.url, {
            "card_number": "4242424242424242",
            "cardholder_name": "JOHN DOE",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "visa",
            "purchase_type": "course",
            "billing_address": "123 Main St",
            "zip_code": "10000",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

    def test_mastercard_with_valid_bin_succeeds(self):
        """Mastercard starting with 51-55 should pass BIN validation."""
        resp = self.client.post(self.url, {
            "card_number": "5555555555554444",
            "cardholder_name": "JANE SMITH",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "mastercard",
            "purchase_type": "course",
            "billing_address": "123 Main St",
            "zip_code": "10000",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

    def test_visa_card_with_wrong_bin_fails(self):
        """Visa payment with non-4 starting card should fail."""
        resp = self.client.post(self.url, {
            "card_number": "5555555555554444",
            "cardholder_name": "JOHN DOE",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "visa",
            "purchase_type": "course",
            "billing_address": "123 Main St",
            "zip_code": "10000",
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get("success"))
        self.assertIn("card_number", data.get("errors", {}))

    def test_mastercard_with_wrong_bin_fails(self):
        """Mastercard payment with Visa BIN should fail."""
        resp = self.client.post(self.url, {
            "card_number": "4242424242424242",
            "cardholder_name": "JOHN DOE",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "mastercard",
            "purchase_type": "course",
            "billing_address": "123 Main St",
            "zip_code": "10000",
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get("success"))
        self.assertIn("card_number", data.get("errors", {}))

    def test_invalid_luhn_checksum_fails(self):
        """Card number with invalid Luhn checksum should fail."""
        resp = self.client.post(self.url, {
            "card_number": "4242424242424241",
            "cardholder_name": "JOHN DOE",
            "expiry_date": "12/30",
            "cvv": "123",
            "card_type": "visa",
            "purchase_type": "course",
            "billing_address": "123 Main St",
            "zip_code": "10000",
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get("success"))
        self.assertIn("card_number", data.get("errors", {}))
