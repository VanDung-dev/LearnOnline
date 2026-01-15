from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods
from ..models import Course, Category
from ..forms import CourseForm
from ..services.search_service import log_search_query


@login_required
def create_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if not title:
            messages.error(request, 'Please enter a course title.')
            return redirect('user_dashboard_with_tab', sub_page='courses')
            
        # Check for duplicate title for this instructor
        if Course.objects.filter(instructor=request.user, title__iexact=title).exists():
             messages.error(request, 'You already have a course with this title.')
             return redirect('user_dashboard_with_tab', sub_page='courses')

        # Create Course
        # We need a category. Find or create default.
        category = Category.objects.first()
        if not category:
             category = Category.objects.create(name="General", description="Default category")
        
        from django.utils.text import slugify
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Course.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        course = Course.objects.create(
            title=title,
            slug=slug,
            instructor=request.user,
            category=category,
            description="",
            price=0,
            certificate_price=0
        )
        
        messages.success(request, 'Course created successfully!')
        return redirect('courses:edit_course', slug=course.slug)
    else:
        # Redirect back to dashboard courses tab if accessed via GET
        return redirect('user_dashboard_with_tab', sub_page='courses')


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
                'redirect_url': '/dashboard/courses/'  # URL to redirect after deletion
            })
        else:
            # Traditional redirect for non-AJAX requests
            messages.success(request, f'Course "{course_title}" has been deleted successfully!')
            return redirect('user_dashboard_with_tab', sub_page='courses')
    
    # For GET requests, redirect back to edit course page
    # This prevents the need for a separate delete confirmation page
    return redirect('courses:edit_course', slug=course.slug)


def course_list(request):
    """
    Display list of courses with search, filter, and sorting functionality.
    
    Query Parameters:
        q: Search query (searches title, description, instructor name)
        category: Filter by category ID
        is_free: Filter free courses only (true/false)
        min_price: Minimum price filter
        max_price: Maximum price filter
        ordering: Sort order (newest, oldest, price_low, price_high, popular)
    """
    from django.db.models import Q, Count
    
    courses = Course.objects.filter(is_active=True)
    
    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        # Log search query
        log_search_query(query, request.user if request.user.is_authenticated else None)

        courses = courses.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__username__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query) |
            Q(category__name__icontains=query)
        )

    
    # Category filter
    category_id = request.GET.get('category', '').strip()
    if category_id and category_id.isdigit():
        courses = courses.filter(category_id=int(category_id))
    
    # Free courses filter
    is_free = request.GET.get('is_free', '').lower()
    if is_free == 'true':
        courses = courses.filter(price=0)
    
    # Price range filters
    min_price = request.GET.get('min_price', '').strip()
    if min_price:
        try:
            courses = courses.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    max_price = request.GET.get('max_price', '').strip()
    if max_price:
        try:
            courses = courses.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Ordering
    ordering = request.GET.get('ordering', 'newest')
    if ordering == 'oldest':
        courses = courses.order_by('created_at')
    elif ordering == 'price_low':
        courses = courses.order_by('price', '-created_at')
    elif ordering == 'price_high':
        courses = courses.order_by('-price', '-created_at')
    elif ordering == 'popular':
        courses = courses.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count', '-created_at')
    else:  # newest (default)
        courses = courses.order_by('-created_at')
    
    # Optimize query
    courses = courses.select_related('category', 'instructor').prefetch_related('sections')
    
    # Get all categories for filter dropdown
    categories = Category.objects.all().order_by('name')
    
    # Pagination - 12 courses per page
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'courses/course_list.html', {
        'courses': page_obj,
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'selected_category': category_id,
        'is_free': is_free == 'true',
        'min_price': min_price,
        'max_price': max_price,
        'ordering': ordering,
    })


def course_detail(request, slug):
    # First get the course without checking is_active
    course = get_object_or_404(Course, slug=slug)
    
    is_enrolled = False
    is_instructor = False
    
    if request.user.is_authenticated:
        # Check if user is the instructor
        is_instructor = (
                hasattr(request.user, 'profile') and
                request.user.profile.is_instructor() and
                course.instructor == request.user
        )
        # Check if user is enrolled
        is_enrolled = course.enrollments.filter(user=request.user).exists()
    
    # If course is not active and user is NOT the instructor, return 404
    if not course.is_active and not is_instructor:
        # We use get_object_or_404 logic here manually to return 404
        from django.http import Http404
        raise Http404("No Course matches the given query.")
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor
    })


@login_required
def course_learning_process(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    is_enrolled = False
    is_instructor = False
    
    if request.user.is_authenticated:
        # Check if user is enrolled
        is_enrolled = course.enrollments.filter(user=request.user).exists()
        # Check if user is the instructor
        is_instructor = (
                hasattr(request.user, 'profile') and
                request.user.profile.is_instructor() and
                course.instructor == request.user
        )
    
    # Only allow enrolled users or instructors to view the learning process
    if not is_enrolled and not is_instructor:
        messages.error(request, 'You must be enrolled in this course to view the learning process.')
        return redirect('courses:course_detail', slug=slug)
    
    # Check if user has certificate
    user_certificate = None
    if is_enrolled:
        user_certificate = course.certificates.filter(user=request.user).first()
    
    # Get sections with optimization
    sections = course.sections.prefetch_related(
        'subsections',
        'subsections__lessons',
        'lessons'
    ).all()
    
    # Process sections to identify legacy lessons (lessons without subsection)
    for section in sections:
        section.has_legacy_lessons = section.lessons.filter(subsection__isnull=True).exists()

    return render(request, 'courses/course_learning_process.html', {
        'course': course,
        'sections': sections,  # Pass processed sections
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
        'user_certificate': user_certificate
    })


@require_http_methods(["POST"])
@login_required
def create_category_ajax(request):
    """
    AJAX view to create a new category
    """
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    
    if not name:
        return JsonResponse({
            'status': 'error',
            'message': 'Category name is required.'
        })
    
    # Check if category already exists
    if Category.objects.filter(name__iexact=name).exists():
        return JsonResponse({
            'status': 'error',
            'message': 'A category with this name already exists.'
        })
    
    # Create new category
    category = Category.objects.create(
        name=name,
        description=description
    )
    
    return JsonResponse({
        'status': 'success',
        'id': category.id,
        'name': category.name,
        'message': 'Category created successfully.'
    })

@require_http_methods(["GET"])
@login_required
def check_course_title(request):
    title = request.GET.get('title', '').strip()
    exists = False
    
    if title:
        exists = Course.objects.filter(instructor=request.user, title__iexact=title).exists()
    
    return JsonResponse({
        'exists': exists,
        'valid': True,
    })
