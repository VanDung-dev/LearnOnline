from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from ..models import Course, Section, Subsection
from ..forms import SubsectionForm


@login_required
def create_subsection(request, course_slug, section_id):
    """Create a new subsection for a section."""
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    if request.method == 'POST':
        form = SubsectionForm(request.POST)
        if form.is_valid():
            subsection = form.save(commit=False)
            subsection.section = section
            subsection.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'status': 'success',
                    'message': 'Subsection created successfully!',
                    'subsection': {
                        'id': subsection.id,
                        'title': subsection.title,
                        'description': subsection.description
                    }
                })
            else:
                # Traditional redirect for non-AJAX requests
                messages.success(request, 'Subsection created successfully!')
                return redirect('courses:edit_course', slug=course.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests with form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error creating subsection. Please check the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Error creating subsection. Please check the form.')
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Subsection creation is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def edit_subsection(request, course_slug, section_id, subsection_id):
    """Edit an existing subsection."""
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)
    subsection = get_object_or_404(Subsection, id=subsection_id, section=section)

    if request.method == 'POST':
        form = SubsectionForm(request.POST, instance=subsection)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'status': 'success',
                    'message': 'Subsection updated successfully!',
                    'subsection': {
                        'id': subsection.id,
                        'title': subsection.title,
                        'description': subsection.description
                    }
                })
            else:
                # Traditional redirect for non-AJAX requests
                messages.success(request, 'Subsection updated successfully!')
                return redirect('courses:edit_course', slug=course.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests with form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error updating subsection. Please check the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Error updating subsection. Please check the form.')
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Subsection editing is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def delete_subsection(request, course_slug, section_id, subsection_id):
    """Delete a subsection from a section."""
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)
    subsection = get_object_or_404(Subsection, id=subsection_id, section=section)

    if request.method == 'POST':
        subsection_title = subsection.title
        subsection.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            return JsonResponse({
                'status': 'success',
                'message': f'Subsection "{subsection_title}" has been deleted successfully!'
            })
        else:
            # Traditional redirect for non-AJAX requests
            messages.success(request, f'Subsection "{subsection_title}" has been deleted successfully!')
            return redirect('courses:edit_course', slug=course.slug)

    # Instead of rendering a separate template, redirect to edit_course
    return redirect('courses:edit_course', slug=course.slug)
