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
            messages.success(request, 'Module created successfully!')
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
            messages.success(request, 'Module updated successfully!')
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
        messages.success(request, f'Module "{module_title}" has been deleted successfully!')
        return redirect('courses:edit_course', slug=course.slug)

    # Instead of rendering a separate template, redirect to edit_course with a delete flag
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def reorder_modules(request, course_slug):
    """
    Handle module reordering via AJAX drag and drop
    """
    print(f"Reorder modules called with course_slug: {course_slug}")
    print(f"Request method: {request.method}")
    print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")

    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    print(f"Found course: {course.title}")

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the ordered module IDs from the request
            module_order = request.POST.getlist('module_order[]')
            print(f"Module order received: {module_order}")

            # Update the order of each module
            for index, module_id in enumerate(module_order):
                Module.objects.filter(id=module_id, course=course).update(order=index)
                print(f"Updated module {module_id} order to {index}")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error in reorder_modules: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
