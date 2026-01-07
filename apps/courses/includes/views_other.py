import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db import models
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from ..models import Course, Lesson, Enrollment, Module, Category


from ..services.search_service import get_popular_search_terms

def home(request):
    categories = Category.objects.all()
    # Show all active courses (regardless of opening date) but respect closing date
    now = timezone.now()
    courses = Course.objects.filter(is_active=True)
    # Filter courses to exclude those that have closed
    courses = courses.filter(
        models.Q(closing_date__isnull=True) | models.Q(closing_date__gte=now)
    )[:6]
    
    popular_searches = get_popular_search_terms(limit=10)

    context = {
        'categories': categories,
        'courses': courses,
        'popular_searches': popular_searches,
    }
    return render(request, 'home.html', context)


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # Check if course is currently open for enrollment
    now = timezone.now()
    if course.closing_date and now > course.closing_date:
        messages.error(request, "Enrollment for this course is closed.")
        return redirect('courses:course_detail', slug=slug)

    # Check if user is already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        messages.success(request, "You have been successfully enrolled in this course.")
    else:
        messages.info(request, "You are already enrolled in this course.")

    return render(request, 'courses/enrollment_success.html', {'course': course})


@login_required
def instructor_courses(request):
    if (not request.user.is_superuser
        and (not hasattr(request.user, 'profile')
        or not (request.user.profile.is_instructor()
        or request.user.profile.is_admin()))
    ):
        return HttpResponseForbidden("You must be an instructor to view this page.")

    courses = Course.objects.filter(instructor=request.user)
    context = {
        'courses': courses,
    }
    return render(request, 'courses/instructor_courses.html', context)


@login_required
def delete_lesson_video(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)

    if request.method == 'POST':
        # Check if lesson has a video file
        if lesson.video_file:
            # Delete the video file
            lesson.video_file.delete()
            lesson.video_file = None
            lesson.save()
            messages.success(request, 'Video file deleted successfully!')
        else:
            messages.info(request, 'No video file found for this lesson.')

    return redirect('courses:edit_course', slug=course.slug)


@login_required
@csrf_exempt
@require_POST
def upload_image(request):
    """
    Handle image uploads from TinyMCE editor in lessons
    """
    # Check if user is an instructor
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'instructor':
        return HttpResponseForbidden("Only instructors can upload images.")

    # Get the uploaded file
    image_file = request.FILES.get('file')

    if not image_file:
        return JsonResponse({'error': 'No file provided'}, status=400)

    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed.'},
                            status=400)

    # Validate file size (limit to 5MB)
    if image_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'File size exceeds 5MB limit'}, status=400)

    # Create directory for lesson images if it doesn't exist
    lesson_images_dir = os.path.join(settings.MEDIA_ROOT, 'lesson_images')
    os.makedirs(lesson_images_dir, exist_ok=True)

    # Save the file
    file_path = os.path.join('lesson_images', image_file.name)
    path = default_storage.save(file_path, ContentFile(image_file.read()))

    # Return the URL of the uploaded image (use forward slashes for URL)
    image_url = settings.MEDIA_URL + path.replace('\\', '/')

    return JsonResponse({'location': image_url})


def support(request):
    """
    Display support page with contact information and FAQ
    """
    return render(request, 'courses/support.html')
