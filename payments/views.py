import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

from courses.models import Course, Enrollment, Certificate
from .models import Payment


@login_required
def payment_page(request, course_slug):
    """
    Display the payment page for a course
    """
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is already enrolled
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    
    # If already enrolled and has certificate, redirect to course
    if enrollment and Certificate.objects.filter(user=request.user, course=course).exists():
        messages.info(request, "You already have access to this course and its certificate.")
        return redirect('courses:lesson_detail', 
                       course_slug=course.slug, 
                       lesson_slug=course.modules.first().lessons.first().slug)
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'amount': float(course.price),
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
def process_payment(request, course_slug):
    """
    Process the payment for a course
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is already enrolled and has certificate
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if enrollment and Certificate.objects.filter(user=request.user, course=course).exists():
        return JsonResponse({'error': 'You already have access to this course'}, status=400)
    
    # Get payment details from form
    card_number = request.POST.get('card_number')
    expiry_date = request.POST.get('expiry_date')
    cvv = request.POST.get('cvv')
    card_type = request.POST.get('card_type')
    
    # Validate card details (in a real app, this would be done by a payment processor)
    if not all([card_number, expiry_date, cvv, card_type]):
        return JsonResponse({'error': 'All card details are required'}, status=400)
    
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
        transaction_id=str(uuid.uuid4()).replace('-', '')[:20].upper()
    )
    
    # If course price is 0, mark as completed immediately
    if course.price == 0:
        payment.status = 'completed'
        payment.save()
    
    # Redirect based on payment status
    if payment.status == 'completed':
        messages.success(request, f'Payment successful! You now have access to {course.title}.')
        # Redirect to first lesson
        first_module = course.modules.first()
        if first_module:
            first_lesson = first_module.lessons.first()
            if first_lesson:
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/courses/{course.slug}/lessons/{first_lesson.slug}/'
                })
    
    return JsonResponse({'error': 'Payment processing failed'}, status=400)


@login_required
def purchase_certificate_payment(request, course_slug):
    """
    Handle payment for certificate purchase
    """
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Check if certificate is free
    if course.is_certificate_free():
        messages.info(request, "Certificate is free for this course.")
        first_module = course.modules.first()
        if first_module:
            first_lesson = first_module.lessons.first()
            if first_lesson:
                return redirect('courses:lesson_detail', 
                               course_slug=course.slug, 
                               lesson_slug=first_lesson.slug)
    
    context = {
        'course': course,
        'certificate_price': float(course.certificate_price),
    }
    return render(request, 'payments/certificate_payment_form.html', context)


@login_required
def process_certificate_payment(request, course_slug):
    """
    Process the payment for a certificate
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Check if already has certificate
    if Certificate.objects.filter(user=request.user, course=course).exists():
        return JsonResponse({'error': 'You already have a certificate for this course'}, status=400)
    
    # Get payment details from form
    card_number = request.POST.get('card_number')
    expiry_date = request.POST.get('expiry_date')
    cvv = request.POST.get('cvv')
    card_type = request.POST.get('card_type')
    
    # Validate card details
    if not all([card_number, expiry_date, cvv, card_type]):
        return JsonResponse({'error': 'All card details are required'}, status=400)
    
    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        course=course,
        enrollment=enrollment,
        amount=course.certificate_price,
        currency='USD',
        status='completed',  # In a real app, this would depend on payment processor response
        payment_method=card_type,
        transaction_id=str(uuid.uuid4()).replace('-', '')[:20].upper()
    )
    
    # If certificate price is 0, mark as completed immediately
    if course.certificate_price == 0:
        payment.status = 'completed'
        payment.save()
    
    # Create certificate if payment successful
    if payment.status == 'completed':
        # Create certificate
        certificate = Certificate.objects.create(
            user=request.user,
            course=course,
            enrollment=enrollment
        )
        
        messages.success(request, f'Certificate payment successful! You now have access to locked content.')
        return JsonResponse({
            'success': True,
            'redirect_url': f'/courses/{course.slug}/'
        })
    
    return JsonResponse({'error': 'Payment processing failed'}, status=400)