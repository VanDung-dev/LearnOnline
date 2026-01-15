import re
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from apps.courses.models import Course, Enrollment, Certificate
from .models import Payment, PaymentLog
from .services.payment_service import get_payment_service, PaymentStatus


def luhn_check(card_number):
    """Luhn algorithm to validate card numbers."""
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    return checksum % 10 == 0


def validate_card_number(card_number, payment_method):
    """Validate card number format and BIN for Visa/Mastercard."""
    digits = re.sub(r'\D', '', card_number or '')
    if len(digits) < 13 or len(digits) > 19:
        return False, 'Card number must be 13-19 digits.'

    # BIN validation
    if payment_method == 'visa' and not digits.startswith('4'):
        return False, 'Visa cards must start with 4.'
    if payment_method == 'mastercard':
        prefix2 = int(digits[:2]) if len(digits) >= 2 else 0
        prefix4 = int(digits[:4]) if len(digits) >= 4 else 0
        if not (51 <= prefix2 <= 55 or 2221 <= prefix4 <= 2720):
            return False, 'Invalid Mastercard number.'

    # Luhn check
    if not luhn_check(digits):
        return False, 'Invalid card number (checksum failed).'

    return True, None


def payment_policy(request):
    """Display payment policy page."""
    return render(request, 'payments/payment_policy.html')


def log_payment_event(payment, event_type, previous_status=None, new_status=None,
                      message='', request=None):
    """Create an audit log entry for a payment event."""
    ip_address = None
    user_agent = ''
    if request:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            ip_address = x_forwarded.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    PaymentLog.objects.create(
        payment=payment,
        event_type=event_type,
        previous_status=previous_status,
        new_status=new_status,
        message=message,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@login_required
def payment_page(request, course_slug, purchase_type='course'):
    """
    Display the payment page for a course or certificate
    """
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is already enrolled
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    
    # If purchasing course and already enrolled with certificate, redirect to course
    if purchase_type == 'course':
        if enrollment and Certificate.objects.filter(user=request.user, course=course).exists():
            messages.info(request, "You already have access to this course and its certificate.")
            return redirect('courses:lesson_detail', 
                           course_slug=course.slug, 
                           lesson_slug=course.sections.first().lessons.first().slug)
    
    # If purchasing certificate, check if user is enrolled in the course
    elif purchase_type == 'certificate':
        if not enrollment:
            messages.error(request, "You need to enroll in the course before purchasing a certificate.")
            return redirect('payments:payment_page', course_slug=course.slug)
            
        # Check if already has certificate
        if Certificate.objects.filter(user=request.user, course=course).exists():
            messages.info(request, "You already have a certificate for this course.")
            return redirect('courses:course_detail', course_slug=course.slug)
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'amount': float(course.price if purchase_type == 'course' else course.certificate_price),
        'purchase_type': purchase_type,
        'certificate_price': float(course.certificate_price) if purchase_type == 'certificate' else None,
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
def process_payment(request, course_slug, purchase_type='course'):
    """
    Process the payment for a course or certificate
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'code': 'invalid_method',
            'message': 'Invalid request method',
            'errors': {},
            'transaction_id': None,
            'redirect_url': None,
        }, status=400)
    
    course = get_object_or_404(Course, slug=course_slug)

    # Check if course has expired
    from django.utils import timezone
    if course.expiration_date and timezone.now() > course.expiration_date:
        return JsonResponse({
            'success': False,
            'code': 'course_expired',
            'message': 'This course has expired and is no longer available for enrollment or certificate purchase.',
            'errors': {},
            'transaction_id': None,
            'redirect_url': None,
        }, status=400)

    # Get payment details from form
    payment_method = request.POST.get('payment_method')
    # fallback for backward compatibility if payment_method not explicitly sent but card_type is
    if not payment_method:
        payment_method = request.POST.get('card_type')
        
    card_number = request.POST.get('card_number')
    cardholder_name = request.POST.get('cardholder_name')
    expiry_date = request.POST.get('expiry_date')
    cvv = request.POST.get('cvv')
    
    billing_address = request.POST.get('billing_address')
    zip_code = request.POST.get('zip_code')
    phone_number = request.POST.get('phone_number')
    email = request.POST.get('email', request.user.email)

    purchase_type = request.POST.get('purchase_type', purchase_type)
    client_token = request.POST.get('client_token')

    # Validate details
    missing_fields = {}
    if not payment_method:
        missing_fields['payment_method'] = ['Please select a payment method.']

    if payment_method in ['visa', 'mastercard']:
        if not card_number:
            missing_fields['card_number'] = ['This field is required.']
        if not cardholder_name or len(cardholder_name.strip()) < 2:
            missing_fields['cardholder_name'] = ['Please enter cardholder name.']
        if not expiry_date:
            missing_fields['expiry_date'] = ['This field is required.']
        if not cvv:
            missing_fields['cvv'] = ['This field is required.']
        
        if not billing_address:
            missing_fields['billing_address'] = ['Please enter billing address.']
        if not zip_code:
            missing_fields['zip_code'] = ['Please enter zip code.']
        if not email:
            missing_fields['email'] = ['Email is required.']
            
    if missing_fields:
        return JsonResponse({
            'success': False,
            'code': 'validation_error',
            'message': 'Invalid or missing fields',
            'errors': missing_fields,
            'transaction_id': None,
            'redirect_url': None,
        }, status=400)

    # Validate card number for Visa/Mastercard (BIN + Luhn check)
    if payment_method in ['visa', 'mastercard'] and card_number:
        is_valid, error_msg = validate_card_number(card_number, payment_method)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'code': 'validation_error',
                'message': 'Invalid card number',
                'errors': {'card_number': [error_msg]},
                'transaction_id': None,
                'redirect_url': None,
            }, status=400)
    
    # Prepare service and idempotency
    service = get_payment_service()
    if not client_token:
        # fallback: generate a server-side token if client didn't send one
        client_token = str(uuid.uuid4())

    # If an idempotent payment exists for this context, re-use it
    existing = Payment.objects.filter(
        user=request.user,
        course=course,
        purchase_type=purchase_type,
        idempotency_key=client_token,
    ).first()
    if existing:
        if existing.status == 'completed':
            success_url = reverse('payments:payment_success', kwargs={'transaction_id': existing.transaction_id})
            return JsonResponse({
                'success': True,
                'code': None,
                'message': 'Payment already completed',
                'errors': {},
                'transaction_id': existing.transaction_id,
                'redirect_url': success_url,
            })
        # If still pending/failed, return a generic response
        return JsonResponse({
            'success': False,
            'code': 'payment_in_progress',
            'message': 'A payment is already in progress for this order. Please wait or try again shortly.',
            'errors': {},
            'transaction_id': existing.transaction_id,
            'redirect_url': None,
        }, status=409)

    # Handle course purchase
    if purchase_type == 'course':
        # Check if user is already enrolled and has certificate
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment and Certificate.objects.filter(user=request.user, course=course).exists():
            return JsonResponse({
                'success': False,
                'code': 'already_enrolled',
                'message': 'You already have access to this course',
                'errors': {},
                'transaction_id': None,
                'redirect_url': None,
            }, status=400)
        
        # Create payment record in pending state (no enrollment yet)
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            enrollment=None,
            amount=course.price,
            currency='USD',
            status='pending',
            payment_method=payment_method,
            purchase_type='course',
            transaction_id=str(uuid.uuid4()).replace('-', '')[:20].upper(),
            idempotency_key=client_token,
        )
        # Log payment creation
        log_payment_event(
            payment, 'created', new_status='pending',
            message=f'Course purchase: {course.title}', request=request
        )

        # Call gateway (mock completes immediately)
        result = service.create_payment(
            user_id=request.user.id,
            course_id=course.id,
            purchase_type='course',
            payment_method=payment_method,
            amount=str(course.price),
            currency=payment.currency,
            idempotency_key=client_token,
            metadata={
                "payment_id": payment.id,
                "cardholder_name": cardholder_name,
                "billing_address": billing_address,
                "zip_code": zip_code,
                "phone_number": phone_number,
                "email": email
            },
        )

        payment.processor_transaction_id = result.processor_transaction_id
        new_status = result.status if result.success else 'failed'
        if payment.status != new_status:
            log_payment_event(
                payment, 'status_change', previous_status='pending',
                new_status=new_status, request=request
            )
        payment.status = new_status
        payment.save()

        if payment.status == 'completed':
            # Create enrollment on success
            enrollment, _ = Enrollment.objects.get_or_create(user=request.user, course=course)
            payment.enrollment = enrollment
            payment.save(update_fields=["enrollment", "updated_at"])
            messages.success(request, f'Payment successful! You now have access to {course.title}.')
            success_url = reverse('payments:payment_success', kwargs={'transaction_id': payment.transaction_id})
            return JsonResponse({
                'success': True,
                'code': None,
                'message': 'Payment processed successfully',
                'errors': {},
                'transaction_id': payment.transaction_id,
                'redirect_url': success_url,
            })
        else:
            return JsonResponse({
                'success': False,
                'code': 'payment_failed',
                'message': result.message or 'Payment failed',
                'errors': {},
                'transaction_id': payment.transaction_id,
                'redirect_url': None,
            }, status=400)
    
    # Handle certificate purchase
    elif purchase_type == 'certificate':
        # Check if user is enrolled
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        
        # Check if already has certificate
        if Certificate.objects.filter(user=request.user, course=course).exists():
            return JsonResponse({
                'success': False,
                'code': 'already_has_certificate',
                'message': 'You already have a certificate for this course',
                'errors': {},
                'transaction_id': None,
                'redirect_url': None,
            }, status=400)
        
        # Create payment record (pending)
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            enrollment=enrollment,  # enrollment exists prior to certificate purchase
            amount=course.certificate_price,
            currency='USD',
            status='pending',
            payment_method=payment_method,
            purchase_type='certificate',
            transaction_id=str(uuid.uuid4()).replace('-', '')[:20].upper(),
            idempotency_key=client_token,
        )
        # Log certificate payment creation
        log_payment_event(
            payment, 'created', new_status='pending',
            message=f'Certificate purchase: {course.title}', request=request
        )

        result = service.create_payment(
            user_id=request.user.id,
            course_id=course.id,
            purchase_type='certificate',
            payment_method=payment_method,
            amount=str(course.certificate_price),
            currency=payment.currency,
            idempotency_key=client_token,
            metadata={
                "payment_id": payment.id,
                "cardholder_name": cardholder_name,
                "billing_address": billing_address,
                "zip_code": zip_code,
                "phone_number": phone_number,
                "email": email
            },
        )

        payment.processor_transaction_id = result.processor_transaction_id
        new_status = result.status if result.success else 'failed'
        if payment.status != new_status:
            log_payment_event(
                payment, 'status_change', previous_status='pending',
                new_status=new_status, request=request
            )
        payment.status = new_status
        payment.save()

        if payment.status == 'completed':
            messages.success(request, 'Certificate payment successful! You now have access to locked content.')
            success_url = reverse('payments:payment_success', kwargs={'transaction_id': payment.transaction_id})
            return JsonResponse({
                'success': True,
                'code': None,
                'message': 'Payment processed successfully',
                'errors': {},
                'transaction_id': payment.transaction_id,
                'redirect_url': success_url,
            })
        else:
            return JsonResponse({
                'success': False,
                'code': 'payment_failed',
                'message': result.message or 'Payment failed',
                'errors': {},
                'transaction_id': payment.transaction_id,
                'redirect_url': None,
            }, status=400)

    return JsonResponse({
        'success': False,
        'code': 'processing_failed',
        'message': 'Payment processing failed',
        'errors': {},
        'transaction_id': None,
        'redirect_url': None,
    }, status=400)


@login_required
def payment_success(request, transaction_id):
    """Render payment success page for the owner of the payment."""
    payment = get_object_or_404(Payment, transaction_id=transaction_id, user=request.user)
    course = payment.course
    # Compute CTA URLs
    first_lesson_url = None
    if course and course.sections.first() and course.sections.first().lessons.first():
        first_lesson = course.sections.first().lessons.first()
        first_lesson_url = f'/courses/{course.slug}/lessons/{first_lesson.slug}/'
    context = {
        'payment': payment,
        'course': course,
        'first_lesson_url': first_lesson_url,
    }
    return render(request, 'payments/payment_success.html', context)


@csrf_exempt
def payment_webhook(request, provider: str):
    """Generic webhook endpoint for payment providers."""
    service = get_payment_service(provider)
    event = service.verify_webhook(request)
    if not event.valid:
        return JsonResponse({"received": False, "message": event.message}, status=400)

    # Update payment by processor_transaction_id if possible
    if event.processor_transaction_id:
        try:
            payment = Payment.objects.get(
                processor_transaction_id=event.processor_transaction_id
            )
            previous_status = payment.status
            valid_statuses = {
                PaymentStatus.COMPLETED, PaymentStatus.FAILED,
                PaymentStatus.REFUNDED, PaymentStatus.PENDING
            }
            if event.status in valid_statuses:
                payment.status = event.status
                payment.save()
                # Log webhook status change
                log_payment_event(
                    payment, 'webhook_received',
                    previous_status=previous_status,
                    new_status=event.status,
                    message=f'Webhook from {provider}'
                )
                # On completion for course, ensure enrollment exists
                if (payment.status == PaymentStatus.COMPLETED
                        and payment.purchase_type == 'course'
                        and not payment.enrollment):
                    enrollment, _ = Enrollment.objects.get_or_create(
                        user=payment.user, course=payment.course
                    )
                    payment.enrollment = enrollment
                    payment.save(update_fields=["enrollment", "updated_at"])
        except Payment.DoesNotExist:
            pass

    return JsonResponse({"received": True})
