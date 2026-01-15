from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from ..models import Course, Section
from ..forms import SectionForm


@login_required
def create_section(request, course_slug):
    """Create a new section for a course."""
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)

    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.course = course
            section.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'status': 'success',
                    'message': 'Section created successfully!',
                    'section': {
                        'id': section.id,
                        'title': section.title,
                        'description': section.description
                    }
                })
            else:
                # Traditional redirect for non-AJAX requests
                messages.success(request, 'Section created successfully!')
                return redirect('courses:edit_course', slug=course.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests with form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error creating section. Please check the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Error creating section. Please check the form.')
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Section creation is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def edit_section(request, course_slug, section_id):
    """Edit an existing section."""
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'status': 'success',
                    'message': 'Section updated successfully!',
                    'section': {
                        'id': section.id,
                        'title': section.title,
                        'description': section.description
                    }
                })
            else:
                # Traditional redirect for non-AJAX requests
                messages.success(request, 'Section updated successfully!')
                return redirect('courses:edit_course', slug=course.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests with form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error updating section. Please check the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Error updating section. Please check the form.')
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Section editing is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def delete_section(request, course_slug, section_id):
    """Delete a section from a course."""
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    if request.method == 'POST':
        section_title = section.title
        section.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            return JsonResponse({
                'status': 'success',
                'message': f'Section "{section_title}" has been deleted successfully!'
            })
        else:
            # Traditional redirect for non-AJAX requests
            messages.success(request, f'Section "{section_title}" has been deleted successfully!')
            return redirect('courses:edit_course', slug=course.slug)

    # Instead of rendering a separate template, redirect to edit_course with a delete flag
    return redirect('courses:edit_course', slug=course.slug)
