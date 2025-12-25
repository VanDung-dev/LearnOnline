from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.conf import settings


class PaymentStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class PaymentResult:
    success: bool
    status: str
    processor_transaction_id: Optional[str]
    message: str = ""
    raw: Optional[Dict[str, Any]] = None


@dataclass
class WebhookEvent:
    valid: bool
    status: Optional[str]
    processor_transaction_id: Optional[str]
    message: str = ""
    raw: Optional[Dict[str, Any]] = None


class PaymentService:
    """Abstract payment service interface. Real gateways should implement this."""

    def create_payment(
        self,
        *,
        user_id: int,
        course_id: Optional[int],
        purchase_type: str,
        amount: str,
        currency: str,
        idempotency_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        raise NotImplementedError

    def verify_webhook(self, request) -> WebhookEvent:
        raise NotImplementedError


class MockPaymentService(PaymentService):
    """Mock driver: behaves like a synchronous gateway that always succeeds."""

    def create_payment(
        self,
        *,
        user_id: int,
        course_id: Optional[int],
        purchase_type: str,
        amount: str,
        currency: str,
        idempotency_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        # In mock, we simply return a completed result with a fake processor id.
        proc_id = f"MOCK-{str(uuid.uuid4()).replace('-', '')[:24].upper()}"
        return PaymentResult(
            success=True,
            status=PaymentStatus.COMPLETED,
            processor_transaction_id=proc_id,
            message="Mock payment approved",
            raw={
                "idempotency_key": idempotency_key,
                "metadata": metadata or {},
            },
        )

    def verify_webhook(self, request) -> WebhookEvent:
        # For mock, accept JSON body with fields: processor_transaction_id, status
        try:
            # very simple shared-secret check
            sig = request.headers.get("X-Payments-Signature")
            secret = getattr(settings, "PAYMENTS_WEBHOOK_SECRET", "dev_secret")
            if not sig or sig != secret:
                return WebhookEvent(False, None, None, message="Invalid signature")

            payload = json.loads(request.body.decode("utf-8") or "{}")
            status = payload.get("status")
            processor_id = payload.get("processor_transaction_id")
            if status not in {
                PaymentStatus.PENDING,
                PaymentStatus.COMPLETED,
                PaymentStatus.FAILED,
                PaymentStatus.REFUNDED,
            }:
                return WebhookEvent(False, None, None, message="Invalid status", raw=payload)
            return WebhookEvent(True, status, processor_id, raw=payload)
        except Exception as e:
            return WebhookEvent(False, None, None, message=str(e))


def get_payment_service(provider: Optional[str] = None) -> PaymentService:
    """Factory returning a payment service instance based on settings or param."""
    driver = (provider or getattr(settings, "PAYMENTS_DRIVER", "mock")).lower()
    # For now we only have mock; real drivers can be added later (stripe, vnpay, momo)
    return MockPaymentService()
