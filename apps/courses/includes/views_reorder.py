from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Course, Lesson, Module, Quiz, Question


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


@login_required
def reorder_lessons(request, course_slug, module_id):
    """
    Handle lesson reordering via AJAX drag and drop
    """
    print(f"Reorder lessons called with course_slug: {course_slug}, module_id: {module_id}")
    print(f"Request method: {request.method}")
    print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")

    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    print(f"Found module: {module.title}")

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the ordered lesson IDs from the request
            lesson_order = request.POST.getlist('lesson_order[]')
            print(f"Lesson order received: {lesson_order}")

            # Update the order of each lesson
            for index, lesson_id in enumerate(lesson_order):
                Lesson.objects.filter(id=lesson_id, module=module).update(order=index)
                print(f"Updated lesson {lesson_id} order to {index}")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error in reorder_lessons: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def reorder_quiz_questions(request, course_slug, module_id, lesson_id):
    """
    Handle quiz question reordering via AJAX drag and drop
    """
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)

    # Ensure lesson has a quiz
    if lesson.lesson_type != 'quiz':
        return JsonResponse({'status': 'error', 'message': 'This lesson is not a quiz'})

    try:
        quiz = lesson.quiz
    except Quiz.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Quiz not found for this lesson'})

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the ordered question IDs from the request
            question_order = request.POST.getlist('question_order[]')

            # Update the order of each question
            for index, question_id in enumerate(question_order):
                Question.objects.filter(id=question_id, quiz=quiz).update(order=index)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})