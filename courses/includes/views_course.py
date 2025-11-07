from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from ..models import Course
from ..forms import CourseForm

@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('courses:edit_course', slug=course.slug)
    else:
        form = CourseForm()
    
    return render(request, 'courses/create_course.html', {'form': form})


@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        # Handle thumbnail deletion
        if 'delete_thumbnail' in request.POST:
            if course.thumbnail:
                # Delete the thumbnail file
                if default_storage.exists(course.thumbnail.name):
                    default_storage.delete(course.thumbnail.name)
                course.thumbnail = None
                course.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Return JSON response for AJAX requests
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Thumbnail deleted successfully!'
                    })
                else:
                    # Traditional redirect for non-AJAX requests
                    messages.success(request, 'Thumbnail deleted successfully!')
                    return redirect('courses:edit_course', slug=course.slug)
        
        # Handle regular form submission
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            # Handle certificate price logic
            course_instance = form.save(commit=False)
            
            # If course price > 0, certificate is automatically free
            if course_instance.price and course_instance.price > 0:
                course_instance.certificate_price = 0
            
            course_instance.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'status': 'success',
                    'message': 'Course updated successfully!'
                })
            else:
                # Traditional redirect for non-AJAX requests
                messages.success(request, 'Course updated successfully!')
                return redirect('courses:edit_course', slug=course.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests with form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error updating course. Please check the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/edit_course.html', {
        'course': course,
        'form': form
    })


@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == 'POST':
        course_title = course.title
        course.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            return JsonResponse({
                'status': 'success',
                'message': f'Course "{course_title}" has been deleted successfully!',
                'redirect_url': '/instructor/courses/'  # URL to redirect after deletion
            })
        else:
            # Traditional redirect for non-AJAX requests
            messages.success(request, f'Course "{course_title}" has been deleted successfully!')
            return redirect('courses:instructor_courses')
    
    # For GET requests, redirect back to edit course page
    # This prevents the need for a separate delete confirmation page
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    is_enrolled = False
    is_instructor = False
    
    if request.user.is_authenticated:
        # Check if user is enrolled
        is_enrolled = course.enrollments.filter(user=request.user).exists()
        # Check if user is the instructor
        is_instructor = (hasattr(request.user, 'profile') and 
                         request.user.profile.is_instructor() and 
                         course.instructor == request.user)
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor
    })


@login_required
def instructor_courses(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor_courses.html', {'courses': courses})