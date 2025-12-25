import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from apps.courses.models import Course, Enrollment, Certificate
from .models import Payment


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
                           lesson_slug=course.modules.first().lessons.first().slug)
    
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
    card_number = request.POST.get('card_number')
    expiry_date = request.POST.get('expiry_date')
    cvv = request.POST.get('cvv')
    card_type = request.POST.get('card_type')
    purchase_type = request.POST.get('purchase_type', purchase_type)  # Get from form if available
    
    # Validate card details (in a real app, this would be done by a payment processor)
    missing_fields = {}
    if not card_number:
        missing_fields['card_number'] = ['This field is required.']
    if not expiry_date:
        missing_fields['expiry_date'] = ['This field is required.']
    if not cvv:
        missing_fields['cvv'] = ['This field is required.']
    if not card_type:
        missing_fields['card_type'] = ['This field is required.']
    if missing_fields:
        return JsonResponse({
            'success': False,
            'code': 'validation_error',
            'message': 'Invalid or missing fields',
            'errors': missing_fields,
            'transaction_id': None,
            'redirect_url': None,
        }, status=400)
    
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
        
        # Create or get enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'enrolled_at': None}  # Will be set automatically
        )
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            enrollment=enrollment,
            amount=course.price,
            currency='USD',
            status='completed',  # In a real app, this would depend on payment processor response
            payment_method=card_type,
            purchase_type='course',
            transaction_id=str(uuid.uuid4()).replace('-', '')[:20].upper()
        )
        
        # If course price is 0, mark as completed immediately
        if course.price == 0:
            payment.status = 'completed'
            payment.save()
        
        # Redirect to success page
        if payment.status == 'completed':
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
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            enrollment=enrollment,
            amount=course.certificate_price,
            currency='USD',
            status='completed',  # In a real app, this would depend on payment processor response
            payment_method=card_type,
            purchase_type='certificate',
            transaction_id=str(uuid.uuid4()).replace('-', '')[:20].upper()
        )
        
        # If certificate price is 0, mark as completed immediately
        if course.certificate_price == 0:
            payment.status = 'completed'
            payment.save()

        # Redirect to success page
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
    if course and course.modules.first() and course.modules.first().lessons.first():
        first_lesson = course.modules.first().lessons.first()
        first_lesson_url = f'/courses/{course.slug}/lessons/{first_lesson.slug}/'
    context = {
        'payment': payment,
        'course': course,
        'first_lesson_url': first_lesson_url,
    }
    return render(request, 'payments/payment_success.html', context)
