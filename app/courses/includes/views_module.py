from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from ..models import Course, Module
from ..forms import ModuleForm

@login_required
def create_module(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'status': 'success',
                    'message': 'Module created successfully!',
                    'module': {
                        'id': module.id,
                        'title': module.title,
                        'description': module.description
                    }
                })
            else:
                # Traditional redirect for non-AJAX requests
                messages.success(request, 'Module created successfully!')
                return redirect('courses:edit_course', slug=course.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests with form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error creating module. Please check the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Error creating module. Please check the form.')
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Module creation is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def edit_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)

    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'status': 'success',
                    'message': 'Module updated successfully!',
                    'module': {
                        'id': module.id,
                        'title': module.title,
                        'description': module.description
                    }
                })
            else:
                # Traditional redirect for non-AJAX requests
                messages.success(request, 'Module updated successfully!')
                return redirect('courses:edit_course', slug=course.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests with form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error updating module. Please check the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Error updating module. Please check the form.')
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Module editing is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def delete_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)

    if request.method == 'POST':
        module_title = module.title
        module.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            return JsonResponse({
                'status': 'success',
                'message': f'Module "{module_title}" has been deleted successfully!'
            })
        else:
            # Traditional redirect for non-AJAX requests
            messages.success(request, f'Module "{module_title}" has been deleted successfully!')
            return redirect('courses:edit_course', slug=course.slug)

    # Instead of rendering a separate template, redirect to edit_course with a delete flag
    return redirect('courses:edit_course', slug=course.slug)
