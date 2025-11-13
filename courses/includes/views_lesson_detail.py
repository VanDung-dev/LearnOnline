from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from ..models import (Course, Lesson, Enrollment, Progress, Certificate,
                      Quiz, Answer, QuizAttempt, UserAnswer)


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
        # Allow instructors to view even if course is closed
        if not (hasattr(request.user, 'profile') and 
                request.user.profile.is_instructor() and 
                course.instructor == request.user):
            raise Http404("Course is not currently available")

    # Check if user is enrolled or is the instructor
    enrollment = None
    is_enrolled = False
    has_certificate = False
    
    # Check if user is the instructor of this course
    is_instructor = (hasattr(request.user, 'profile') and 
                     request.user.profile.is_instructor() and 
                     course.instructor == request.user)
    
    if not is_instructor:
        # Regular student logic
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        is_enrolled = True
        has_certificate = Certificate.objects.filter(user=request.user, course=course).exists()
    else:
        # For instructors, treat as enrolled but without certificate
        is_enrolled = True

    # Add debugging information
    if lesson.lesson_type == 'video' and not lesson.video_url:
        logger = logging.getLogger(__name__)
        logger.warning(f"Video lesson '{lesson.title}' (ID: {lesson.id}) has no video URL set")

    # Check if lesson/module is locked - instructors can always access
    if not is_instructor and (lesson.is_locked or lesson.module.is_locked) and not has_certificate:
        # Lesson or module is locked and user doesn't have certificate
        messages.error(request, "This content is locked. Purchase a certificate to access it.")
        return redirect('courses:course_detail', slug=course.slug)

    # Handle quiz lessons
    if lesson.lesson_type == 'quiz':
        # Check if quiz exists
        try:
            quiz = lesson.quiz
        except Quiz.DoesNotExist:
            if not is_instructor:
                messages.error(request, "This quiz is not configured yet.")
                return redirect('courses:course_detail', slug=course.slug)
            else:
                # For instructors, continue to show the lesson detail page
                quiz = None

        # Students: Check if already submitted
        if not is_instructor:
            submitted_attempt = QuizAttempt.objects.filter(
                user=request.user,
                lesson=lesson,
                completed_at__isnull=False
            ).first()

            if submitted_attempt:
                # User has already submitted, show results only
                context = {
                    'course': course,
                    'lesson': lesson,
                    'quiz': quiz,
                    'attempt': submitted_attempt,
                    'already_submitted': True,
                    'is_instructor': is_instructor,
                }
                return render(request, 'courses/lesson_detail.html', context)

        if request.method == 'POST' and not is_instructor:
            # Get or create current attempt
            current_attempt = QuizAttempt.objects.filter(
                user=request.user,
                lesson=lesson,
                completed_at__isnull=True
            ).first()

            if not current_attempt:
                current_attempt = QuizAttempt.objects.create(
                    user=request.user,
                    lesson=lesson,
                    attempt_number=1
                )

            # Initialize check count in session if not exists
            session_key = f'quiz_check_count_{lesson.id}'
            if session_key not in request.session:
                request.session[session_key] = 0

            # Handle Check Answers
            if 'check_answers' in request.POST:
                # Increment check count
                request.session[session_key] += 1
                check_count = request.session[session_key]

                # Calculate score temporarily
                score = 0
                total_points = 0
                check_results = {}

                for question in quiz.questions.all():
                    if question.question_type in ['single', 'multiple']:
                        if question.question_type == 'single':
                            answer_id = request.POST.get(f'question_{question.id}')
                            if answer_id:
                                try:
                                    selected_answer = Answer.objects.get(id=answer_id, question=question)
                                    check_results[question.id] = {
                                        'selected': [selected_answer.id],
                                        'correct': selected_answer.is_correct
                                    }
                                    if selected_answer.is_correct:
                                        score += question.points
                                except Answer.DoesNotExist:
                                    pass
                        elif question.question_type == 'multiple':
                            answer_ids = request.POST.getlist(f'question_{question.id}')
                            if answer_ids:
                                selected_answers = Answer.objects.filter(id__in=answer_ids, question=question)
                                correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
                                selected_answer_ids = set(selected_answers.values_list('id', flat=True))

                                check_results[question.id] = {
                                    'selected': list(selected_answer_ids),
                                    'correct': correct_answers == selected_answer_ids
                                }

                                if correct_answers == selected_answer_ids:
                                    score += question.points

                        total_points += question.points

                temp_score = (score / total_points * 100) if total_points > 0 else 0

                # Check if max_check reached, auto submit
                remaining_checks = lesson.max_check - check_count if lesson.max_check > 0 else -1

                if lesson.max_check > 0 and check_count >= lesson.max_check:
                    # Auto submit
                    messages.warning(request, f"You have used all {lesson.max_check} checks. Auto-submitting your quiz...")
                    # Process final submission (reuse submission code below)
                    request.POST = request.POST.copy()
                    request.POST['submit_quiz'] = 'true'
                else:
                    messages.info(request, f"Temporary Score: {temp_score:.2f}%. Remaining checks: {remaining_checks if remaining_checks >= 0 else 'Unlimited'}")

                    context = {
                        'course': course,
                        'lesson': lesson,
                        'quiz': quiz,
                        'attempt': current_attempt,
                        'check_results': check_results,
                        'temp_score': temp_score,
                        'remaining_checks': remaining_checks,
                        'is_instructor': is_instructor,
                        'user_answers': request.POST,
                    }
                    return render(request, 'courses/lesson_detail.html', context)

            # Handle Submit Quiz (final submission)
            if 'submit_quiz' in request.POST or (lesson.max_check > 0 and request.session.get(session_key, 0) >= lesson.max_check):
                # Use current_attempt for final submission
                new_attempt = current_attempt

                score = 0
                total_points = 0

                for question in quiz.questions.all():
                    # Get selected answers (only for single/multiple choice)
                    if question.question_type == 'single':
                        answer_id = request.POST.get(f'question_{question.id}')
                        if answer_id:
                            try:
                                selected_answer = Answer.objects.get(id=answer_id, question=question)
                                # Save user answer
                                user_answer, created = UserAnswer.objects.get_or_create(
                                    quiz_attempt=new_attempt,
                                    question=question
                                )
                                user_answer.selected_answers.clear()
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
                            user_answer, created = UserAnswer.objects.get_or_create(
                                quiz_attempt=new_attempt,
                                question=question
                            )
                            user_answer.selected_answers.set(selected_answers)

                            # Check if all selected answers are correct and no incorrect answers are selected
                            correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
                            selected_answer_ids = set(selected_answers.values_list('id', flat=True))

                            if correct_answers == selected_answer_ids:
                                score += question.points
                            total_points += question.points

                # Calculate and save score
                if total_points > 0:
                    new_attempt.score = (score / total_points) * 100
                else:
                    new_attempt.score = 0
                new_attempt.completed_at = timezone.now()
                new_attempt.save()

                # Clear session check count
                if session_key in request.session:
                    del request.session[session_key]

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

                # Redirect to the same page but with the completed attempt
                context = {
                    'course': course,
                    'lesson': lesson,
                    'quiz': quiz,
                    'attempt': new_attempt,
                    'already_submitted': True,
                    'is_instructor': is_instructor,
                }
                return render(request, 'courses/lesson_detail.html', context)
        elif not is_instructor:
            # Show quiz form for students (GET request)
            # Get or create an attempt for the student
            current_attempt = QuizAttempt.objects.filter(
                user=request.user,
                lesson=lesson,
                completed_at__isnull=True
            ).first()

            if not current_attempt:
                current_attempt = QuizAttempt.objects.create(
                    user=request.user,
                    lesson=lesson,
                    attempt_number=1
                )

            # Calculate remaining checks
            session_key = f'quiz_check_count_{lesson.id}'
            check_count = request.session.get(session_key, 0)
            remaining_checks = lesson.max_check - check_count if lesson.max_check > 0 else -1

            context = {
                'course': course,
                'lesson': lesson,
                'quiz': quiz,
                'attempt': current_attempt,
                'remaining_checks': remaining_checks,
                'is_instructor': is_instructor,
            }
            return render(request, 'courses/lesson_detail.html', context)
        else:
            # Show quiz preview for instructors
            context = {
                'course': course,
                'lesson': lesson,
                'quiz': quiz,
                'is_instructor': is_instructor,
            }
            return render(request, 'courses/lesson_detail.html', context)

    # Mark lesson as completed (for non-quiz lessons) - only for students
    if not is_instructor:
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
        'is_instructor': is_instructor,
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