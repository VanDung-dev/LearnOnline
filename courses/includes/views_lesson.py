from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from ..models import Course, Lesson, Module, Quiz, Answer, Question
from ..forms import LessonForm, QuizForm


@login_required
def create_lesson(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Lesson created successfully!')

            # Redirect based on lesson type for further configuration
            if lesson.lesson_type == 'quiz':
                # Redirect to quiz configuration page
                messages.info(request, 'You can now configure your quiz questions.')
                return redirect('courses:configure_quiz', lesson_id=lesson.id)
            else:
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Lesson creation is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


@login_required
def edit_lesson(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)

    # Get or create quiz for this lesson if it's a quiz type
    if lesson.lesson_type == 'quiz':
        quiz, created = Quiz.objects.get_or_create(lesson=lesson, defaults={'title': f'Quiz for {lesson.title}'})
    else:
        quiz = None

    if request.method == 'POST':
        # Handle quiz configuration actions
        action = request.POST.get('action')
        
        if action == 'add_question' and lesson.lesson_type == 'quiz':
            # Add new question
            question_text = request.POST.get('question_text')
            question_type = request.POST.get('question_type', 'single')
            points = request.POST.get('points', 1)
            order = request.POST.get('order', 0)

            if question_text:
                question = Question.objects.create(
                    quiz=quiz,
                    text=question_text,
                    question_type=question_type,
                    points=points,
                    order=order
                )

                # Add answers if not an essay question
                if question_type != 'essay':
                    answer_texts = request.POST.getlist('new_answer_text[]')
                    answer_corrects = request.POST.getlist('new_answer_correct[]')

                    for i, answer_text in enumerate(answer_texts):
                        if answer_text:
                            is_correct = str(i) in answer_corrects if answer_corrects else False
                            Answer.objects.create(
                                question=question,
                                text=answer_text,
                                is_correct=is_correct
                            )

                messages.success(request, 'Question added successfully!')
            else:
                messages.error(request, 'Question text is required!')
            
            # Refresh the page to show updated content
            return redirect('courses:edit_lesson', course_slug=course.slug, module_id=module.id, lesson_id=lesson.id)
            
        elif action == 'edit_question' and lesson.lesson_type == 'quiz':
            # Edit existing question
            question_id = request.POST.get('question_id')
            question = get_object_or_404(Question, id=question_id, quiz=quiz)

            question.text = request.POST.get('question_text', question.text)
            question.question_type = request.POST.get('question_type', question.question_type)
            question.points = request.POST.get('points', question.points)
            question.order = request.POST.get('order', question.order)
            question.save()

            # Update existing answers
            for answer in question.answers.all():
                answer_text_key = f'answer_text_{answer.id}'
                answer_correct_key = f'answer_correct_{answer.id}'

                if answer_text_key in request.POST:
                    answer.text = request.POST[answer_text_key]
                    answer.is_correct = answer_correct_key in request.POST
                    answer.save()

            # Add new answers
            if question.question_type != 'essay':
                new_answer_texts = request.POST.getlist(f'new_answer_text_{question.id}[]')
                new_answer_corrects = request.POST.getlist(f'new_answer_correct_{question.id}[]')

                for i, answer_text in enumerate(new_answer_texts):
                    if answer_text:
                        is_correct = str(i) in new_answer_corrects if new_answer_corrects else False
                        Answer.objects.create(
                            question=question,
                            text=answer_text,
                            is_correct=is_correct
                        )

            messages.success(request, 'Question updated successfully!')
            return redirect('courses:edit_lesson', course_slug=course.slug, module_id=module.id, lesson_id=lesson.id)
            
        elif action == 'delete_question' and lesson.lesson_type == 'quiz':
            # Delete question
            question_id = request.POST.get('question_id')
            question = get_object_or_404(Question, id=question_id, quiz=quiz)
            question.delete()
            messages.success(request, 'Question deleted successfully!')
            return redirect('courses:edit_lesson', course_slug=course.slug, module_id=module.id, lesson_id=lesson.id)
            
        elif action is None and lesson.lesson_type == 'quiz':
            # Update quiz details
            quiz_form = QuizForm(request.POST, instance=quiz)
            if quiz_form.is_valid():
                quiz_form.save()
                # Also update lesson max_attempts if provided
                max_attempts = request.POST.get('max_attempts')
                if max_attempts is not None:
                    lesson.max_attempts = max_attempts
                    lesson.save()
                messages.success(request, 'Quiz updated successfully!')
            else:
                messages.error(request, 'Error updating quiz!')
            return redirect('courses:edit_lesson', course_slug=course.slug, module_id=module.id, lesson_id=lesson.id)
            
        else:
            # Handle lesson form
            form = LessonForm(request.POST, request.FILES, instance=lesson)
            if form.is_valid():
                lesson = form.save()
                messages.success(request, 'Lesson updated successfully!')

                # Redirect based on lesson type for further configuration
                if lesson.lesson_type == 'quiz':
                    # Redirect to quiz configuration page
                    messages.info(request, 'You can now configure your quiz questions.')
                    return redirect('courses:edit_lesson', course_slug=course.slug, module_id=module.id, lesson_id=lesson.id)
                else:
                    return redirect('courses:edit_course', slug=course.slug)
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = LessonForm(instance=lesson)

    context = {
        'course': course,
        'module': module,
        'lesson': lesson,
        'form': form,
    }
    return render(request, 'courses/edit_lesson.html', context)


@login_required
def delete_lesson(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)

    if request.method == 'POST':
        lesson_title = lesson.title
        lesson.delete()
        messages.success(request, f'Lesson "{lesson_title}" has been deleted successfully!')
        return redirect('courses:edit_course', slug=course.slug)

    # Instead of rendering a separate template, redirect to edit_course with a delete flag
    return redirect('courses:edit_course', slug=course.slug)


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