from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Course, Lesson, Section, Subsection, Quiz, Question


@login_required
def reorder_sections(request, course_slug):
    """
    Handle section reordering via AJAX drag and drop
    """
    print(f"Reorder sections called with course_slug: {course_slug}")
    print(f"Request method: {request.method}")
    print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")

    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    print(f"Found course: {course.title}")

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the ordered section IDs from the request
            section_order = request.POST.getlist('section_order[]')
            print(f"Section order received: {section_order}")

            # Update the order of each section
            for index, section_id in enumerate(section_order):
                Section.objects.filter(id=section_id, course=course).update(order=index)
                print(f"Updated section {section_id} order to {index}")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error in reorder_sections: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def reorder_subsections(request, course_slug, section_id):
    """
    Handle subsection reordering via AJAX drag and drop
    """
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the ordered subsection IDs from the request
            subsection_order = request.POST.getlist('subsection_order[]')

            # Update the order of each subsection
            for index, subsection_id in enumerate(subsection_order):
                Subsection.objects.filter(id=subsection_id, section=section).update(order=index)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def reorder_lessons(request, course_slug, section_id):
    """
    Handle lesson reordering via AJAX drag and drop
    """
    print(f"Reorder lessons called with course_slug: {course_slug}, section_id: {section_id}")
    print(f"Request method: {request.method}")
    print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")

    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)
    print(f"Found section: {section.title}")

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the ordered lesson IDs from the request
            lesson_order = request.POST.getlist('lesson_order[]')
            print(f"Lesson order received: {lesson_order}")

            # Update the order of each lesson
            for index, lesson_id in enumerate(lesson_order):
                Lesson.objects.filter(id=lesson_id, section=section).update(order=index)
                print(f"Updated lesson {lesson_id} order to {index}")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error in reorder_lessons: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def reorder_subsection_lessons(request, course_slug, section_id, subsection_id):
    """
    Handle lesson reordering within a subsection via AJAX drag and drop
    """
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)
    subsection = get_object_or_404(Subsection, id=subsection_id, section=section)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the ordered lesson IDs from the request
            lesson_order = request.POST.getlist('lesson_order[]')

            # Update the order of each lesson
            for index, lesson_id in enumerate(lesson_order):
                Lesson.objects.filter(id=lesson_id, subsection=subsection).update(order=index)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def reorder_quiz_questions(request, course_slug, section_id, lesson_id):
    """
    Handle quiz question reordering via AJAX drag and drop
    """
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, section=section)

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