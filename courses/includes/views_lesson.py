from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.utils import timezone
from ..models import Course, Lesson, Enrollment, Progress, Module, Certificate, Quiz, Answer, QuizAttempt, UserAnswer
from ..forms import LessonForm


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

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully!')

            # Redirect based on lesson type for further configuration
            if lesson.lesson_type == 'quiz':
                # Redirect to quiz configuration page
                messages.info(request, 'You can now configure your quiz questions.')
                return redirect('courses:configure_quiz', lesson_id=lesson.id)
            else:
                return redirect('courses:edit_course', slug=course.slug)

    # Redirect back to the edit course page instead of rendering a separate template
    messages.info(request, 'Lesson editing is now handled through the course edit page.')
    return redirect('courses:edit_course', slug=course.slug)


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
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    # First get all lessons with the given slug in this course
    lessons = Lesson.objects.filter(slug=lesson_slug, module__course=course, is_published=True)
    if not lessons.exists():
        raise Http404("Lesson not found")
    elif lessons.count() > 1:
        # If multiple lessons with same slug, get the first one
        lesson = lessons.first()
        # Log this issue for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Multiple lessons found with slug '{lesson_slug}' in course '{course.title}'")
    else:
        lesson = lessons.first()

    # Check if course is currently open
    now = timezone.now()
    if ((course.opening_date and now < course.opening_date) or
            (course.closing_date and now > course.closing_date)):
        raise Http404("Course is not currently available")

    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    is_enrolled = True

    # Check if lesson or module is locked
    has_certificate = Certificate.objects.filter(user=request.user, course=course).exists()

    # Add debugging information
    if lesson.lesson_type == 'video' and not lesson.video_url:
        logger = logging.getLogger(__name__)
        logger.warning(f"Video lesson '{lesson.title}' (ID: {lesson.id}) has no video URL set")

    if (lesson.is_locked or lesson.module.is_locked) and not has_certificate:
        # Lesson or module is locked and user doesn't have certificate
        messages.error(request, "This content is locked. Purchase a certificate to access it.")
        return redirect('courses:course_detail', slug=course.slug)

    # Handle quiz lessons
    if lesson.lesson_type == 'quiz':
        # Check if quiz exists
        try:
            quiz = lesson.quiz
        except Quiz.DoesNotExist:
            messages.error(request, "This quiz is not configured yet.")
            return redirect('courses:course_detail', slug=course.slug)

        # Check attempts
        attempts = QuizAttempt.objects.filter(user=request.user, lesson=lesson)
        attempt_count = attempts.count()

        # Check if user has exceeded max attempts
        if lesson.max_attempts > 0 and attempt_count >= lesson.max_attempts:
            messages.error(request,
                           f"You have reached the maximum number of attempts ({lesson.max_attempts}) for this quiz.")
            # Show previous attempts
            context = {
                'course': course,
                'lesson': lesson,
                'quiz': quiz,
                'attempts': attempts,
                'max_attempts_reached': True,
            }
            return render(request, 'courses/lesson_detail.html', context)

        # Create a new attempt
        new_attempt = QuizAttempt.objects.create(
            user=request.user,
            lesson=lesson,
            attempt_number=attempt_count + 1
        )

        if request.method == 'POST':
            # Process quiz submission
            score = 0
            total_points = 0

            for question in quiz.questions.all():
                # Get selected answers
                if question.question_type == 'single':
                    answer_id = request.POST.get(f'question_{question.id}')
                    if answer_id:
                        try:
                            selected_answer = Answer.objects.get(id=answer_id, question=question)
                            # Save user answer
                            user_answer = UserAnswer.objects.create(quiz_attempt=new_attempt, question=question)
                            user_answer.selected_answers.add(selected_answer)

                            # Check if answer is correct
                            if selected_answer.is_correct:
                                score += question.points
                            total_points += question.points
                        except Answer.DoesNotExist:
                            pass
                elif question.question_type == 'multiple':
                    answer_ids = request.POST.getlist(f'question_{question.id}')
                    if answer_ids:
                        selected_answers = Answer.objects.filter(id__in=answer_ids, question=question)
                        # Save user answers
                        user_answer = UserAnswer.objects.create(quiz_attempt=new_attempt, question=question)
                        user_answer.selected_answers.set(selected_answers)

                        # Check if all selected answers are correct and no incorrect answers are selected
                        correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
                        selected_answer_ids = set(selected_answers.values_list('id', flat=True))

                        if correct_answers == selected_answer_ids:
                            score += question.points
                        total_points += question.points
                elif question.question_type == 'essay':
                    # Handle essay questions
                    essay_answer = request.POST.get(f'question_{question.id}')
                    if essay_answer:
                        # Save essay answer in the selected_answers field as a special "answer"
                        essay_answer_obj, created = Answer.objects.get_or_create(
                            question=question,
                            text=essay_answer,
                            defaults={'is_correct': False}  # Essays are manually graded
                        )
                        user_answer = UserAnswer.objects.create(quiz_attempt=new_attempt, question=question)
                        user_answer.selected_answers.add(essay_answer_obj)

                        # For essay questions, we don't automatically score them
                        # They need to be manually graded by the instructor
                        total_points += question.points

            # Calculate and save score
            if total_points > 0:
                new_attempt.score = (score / total_points) * 100
            else:
                new_attempt.score = 0
            new_attempt.completed_at = timezone.now()
            new_attempt.save()

            # Mark lesson as completed if score is high enough (e.g., 70%)
            if new_attempt.score >= 70:
                progress, created = Progress.objects.get_or_create(
                    user=request.user,
                    lesson=lesson
                )
                if not progress.completed:
                    progress.completed = True
                    progress.completed_at = timezone.now()
                    progress.save()

                # Check if course is completed and issue certificate if needed
                check_and_issue_certificate(request.user, course)

                messages.success(request, f"Quiz submitted successfully! Your score: {new_attempt.score:.2f}%")
            else:
                messages.info(request,
                              f"Quiz submitted. Your score: {new_attempt.score:.2f}%. You need at least 70% to pass.")

            return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=lesson.slug)
        else:
            # Show quiz form
            context = {
                'course': course,
                'lesson': lesson,
                'quiz': quiz,
                'attempt': new_attempt,
            }
            return render(request, 'courses/quiz_detail.html', context)

    # Mark lesson as completed (for non-quiz lessons)
    progress, created = Progress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    if not progress.completed:
        progress.completed = True
        progress.save()

    # Check if course is completed and issue certificate if needed
    check_and_issue_certificate(request.user, course)

    # Get next and previous lessons
    all_lessons = Lesson.objects.filter(module__course=course, is_published=True)
    all_lessons_list = list(all_lessons)
    try:
        current_index = all_lessons_list.index(lesson)

        prev_lesson = None
        next_lesson = None

        if current_index > 0:
            prev_lesson = all_lessons_list[current_index - 1]

        if current_index < len(all_lessons_list) - 1:
            next_lesson = all_lessons_list[current_index + 1]
    except ValueError:
        # In case the lesson is not in the list (shouldn't happen but just in case)
        prev_lesson = None
        next_lesson = None

    context = {
        'course': course,
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'enrollment': enrollment,
    }
    return render(request, 'courses/lesson_detail.html', context)


def check_and_issue_certificate(user, course):
    """
    Check if user has completed all lessons in a course and issue certificate if so
    """
    # Get all lessons in the course
    all_lessons = Lesson.objects.filter(module__course=course, is_published=True)
    total_lessons = all_lessons.count()

    if total_lessons == 0:
        return  # No lessons to complete

    # Get completed lessons for this user in this course
    completed_lessons = Progress.objects.filter(
        user=user,
        lesson__in=all_lessons,
        completed=True
    ).count()

    # Check if all lessons are completed
    if completed_lessons == total_lessons:
        # Get enrollment
        enrollment = get_object_or_404(Enrollment, user=user, course=course)

        # Mark enrollment as completed
        if not enrollment.is_completed:
            enrollment.is_completed = True
            enrollment.save()

        # Check if the course has expired
        if course.expiration_date and timezone.now() > course.expiration_date:
            # Course has expired, don't issue certificate
            return

        # Create certificate if it doesn't exist and course hasn't expired
        certificate, created = Certificate.objects.get_or_create(
            user=user,
            course=course,
            enrollment=enrollment
        )

        if created:
            # Notify user about certificate
            pass  # We could send a message here if needed