from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404, JsonResponse
from django.contrib import messages
from django.db import models
from django.utils import timezone
from django.db.models import Q
from .models import Category, Course, Lesson, Enrollment, Progress, Module, Certificate, Quiz, Question, Answer, QuizAttempt, UserAnswer
from .forms import CourseForm, ModuleForm, LessonForm, QuizForm, QuestionForm, AnswerForm


def public_certificate(request, certificate_id):
    """
    Public view for certificate verification.
    Anyone with the certificate ID can view the certificate.
    """
    certificate = get_object_or_404(Certificate, certificate_number=certificate_id)
    
    context = {
        'certificate': certificate,
        'is_public': True,
    }
    return render(request, 'courses/certificate.html', context)


@login_required
def purchase_certificate(request, slug):
    """
    Redirect to payment system for certificate purchase
    """
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Check if certificate is free
    if course.is_certificate_free():
        messages.info(request, "Certificate is free for this course.")
        first_module = course.modules.first()
        if first_module:
            first_lesson = first_module.lessons.first()
            if first_lesson:
                return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=first_lesson.slug)
    
    # Redirect to payment system
    return redirect('payments:purchase_certificate_payment', course_slug=slug)


def home(request):
    categories = Category.objects.all()
    # Show all active courses (regardless of opening date) but respect closing date
    now = timezone.now()
    courses = Course.objects.filter(is_active=True)
    # Filter courses to exclude those that have closed
    courses = courses.filter(
        models.Q(closing_date__isnull=True) | models.Q(closing_date__gte=now)
    )[:6]
    
    context = {
        'categories': categories,
        'courses': courses,
    }
    return render(request, 'courses/home.html', context)


def course_list(request):
    # Only show courses that are currently open
    now = timezone.now()
    courses = Course.objects.filter(is_active=True)

    # Filter courses to exclude those that have closed
    courses = courses.filter(
        models.Q(closing_date__isnull=True) | models.Q(closing_date__gte=now)
    )
    
    # Handle search
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(instructor__username__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query)
        ).distinct()
    
    context = {
        'courses': courses,
        'query': query,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if course is currently available for viewing (not closed)
    now = timezone.now()
    if course.closing_date and now > course.closing_date:
        # Course has closed
        raise Http404("Course is not currently available")
    
    # Check if user is enrolled in the course
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if course is currently open for enrollment
    now = timezone.now()
    if course.closing_date and now > course.closing_date:
        messages.error(request, "Enrollment for this course is closed.")
        return redirect('courses:course_detail', slug=slug)
    
    # Check if user is already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        messages.success(request, "You have been successfully enrolled in this course.")
    else:
        messages.info(request, "You are already enrolled in this course.")
    
    return render(request, 'courses/enrollment_success.html', {'course': course})


@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, module__course=course)
    
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
            messages.error(request, f"You have reached the maximum number of attempts ({lesson.max_attempts}) for this quiz.")
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
                else:  # multiple choice
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
                messages.info(request, f"Quiz submitted. Your score: {new_attempt.score:.2f}%. You need at least 70% to pass.")
            
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
    current_index = list(all_lessons).index(lesson)
    
    prev_lesson = None
    next_lesson = None
    
    if current_index > 0:
        prev_lesson = all_lessons[current_index - 1]
    
    if current_index < len(all_lessons) - 1:
        next_lesson = all_lessons[current_index + 1]
    
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


# Instructor views
@login_required
def instructor_courses(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor():
        return HttpResponseForbidden("You must be an instructor to view this page.")
    
    courses = Course.objects.filter(instructor=request.user)
    context = {
        'courses': courses,
    }
    return render(request, 'courses/instructor_courses.html', context)


@login_required
def create_course(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor():
        return HttpResponseForbidden("You must be an instructor to create courses.")
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('courses:instructor_courses')
    else:
        form = CourseForm()
    
    context = {
        'form': form,
    }
    return render(request, 'courses/create_course.html', context)


@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:instructor_courses')
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/edit_course.html', context)


@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f'Course "{course_title}" has been deleted successfully!')
        return redirect('courses:instructor_courses')
    
    context = {
        'course': course,
    }
    return render(request, 'courses/delete_course.html', context)


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
    else:
        form = ModuleForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/create_module.html', context)


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
    else:
        form = ModuleForm(instance=module)
    
    context = {
        'form': form,
        'course': course,
        'module': module,
    }
    return render(request, 'courses/edit_module.html', context)


@login_required
def delete_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if request.method == 'POST':
        module_title = module.title
        module.delete()
        messages.success(request, f'Module "{module_title}" has been deleted successfully!')
        return redirect('courses:edit_course', slug=course.slug)
    
    context = {
        'course': course,
        'module': module,
    }
    return render(request, 'courses/delete_module.html', context)


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
    else:
        form = LessonForm()
    
    context = {
        'form': form,
        'course': course,
        'module': module,
    }
    return render(request, 'courses/create_lesson.html', context)


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
    else:
        form = LessonForm(instance=lesson)
    
    context = {
        'form': form,
        'course': course,
        'module': module,
        'lesson': lesson,
    }
    return render(request, 'courses/create_lesson.html', context)


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
    
    context = {
        'course': course,
        'module': module,
        'lesson': lesson,
    }
    return render(request, 'courses/delete_lesson.html', context)


@login_required
def configure_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    
    # Get or create quiz for this lesson
    quiz, created = Quiz.objects.get_or_create(lesson=lesson, defaults={'title': f'Quiz for {lesson.title}'})
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('courses:configure_quiz', lesson_id=lesson.id)
    else:
        form = QuizForm(instance=quiz)
    
    context = {
        'lesson': lesson,
        'quiz': quiz,
        'form': form,
    }
    return render(request, 'courses/configure_quiz.html', context)


@login_required
def add_question(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    quiz, created = Quiz.objects.get_or_create(lesson=lesson, defaults={'title': f'Quiz for {lesson.title}'})
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('courses:configure_quiz', lesson_id=lesson.id)
    else:
        form = QuestionForm()
    
    context = {
        'lesson': lesson,
        'quiz': quiz,
        'form': form,
    }
    return render(request, 'courses/add_question.html', context)


@login_required
def edit_question(request, lesson_id, question_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    question = get_object_or_404(Question, id=question_id, quiz__lesson=lesson)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('courses:configure_quiz', lesson_id=lesson.id)
    else:
        form = QuestionForm(instance=question)
    
    context = {
        'lesson': lesson,
        'question': question,
        'form': form,
    }
    return render(request, 'courses/edit_question.html', context)


@login_required
def delete_question(request, lesson_id, question_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    question = get_object_or_404(Question, id=question_id, quiz__lesson=lesson)
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('courses:configure_quiz', lesson_id=lesson.id)
    
    context = {
        'lesson': lesson,
        'question': question,
    }
    return render(request, 'courses/delete_question.html', context)


@login_required
def add_answer(request, lesson_id, question_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    question = get_object_or_404(Question, id=question_id, quiz__lesson=lesson)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            messages.success(request, 'Answer added successfully!')
            return redirect('courses:edit_question', lesson_id=lesson.id, question_id=question.id)
    else:
        form = AnswerForm()
    
    context = {
        'lesson': lesson,
        'question': question,
        'form': form,
    }
    return render(request, 'courses/add_answer.html', context)


@login_required
def edit_answer(request, lesson_id, question_id, answer_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    question = get_object_or_404(Question, id=question_id, quiz__lesson=lesson)
    answer = get_object_or_404(Answer, id=answer_id, question=question)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Answer updated successfully!')
            return redirect('courses:edit_question', lesson_id=lesson.id, question_id=question.id)
    else:
        form = AnswerForm(instance=answer)
    
    context = {
        'lesson': lesson,
        'question': question,
        'answer': answer,
        'form': form,
    }
    return render(request, 'courses/edit_answer.html', context)


@login_required
def delete_answer(request, lesson_id, question_id, answer_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    question = get_object_or_404(Question, id=question_id, quiz__lesson=lesson)
    answer = get_object_or_404(Answer, id=answer_id, question=question)
    
    if request.method == 'POST':
        answer.delete()
        messages.success(request, 'Answer deleted successfully!')
        return redirect('courses:edit_question', lesson_id=lesson.id, question_id=question.id)
    
    context = {
        'lesson': lesson,
        'question': question,
        'answer': answer,
    }
    return render(request, 'courses/delete_answer.html', context)


def course_certificate(request, certificate_id):
    """
    View for certificate verification.
    If user is authenticated, they can view their own certificate.
    For public access, anyone with the certificate ID can view the certificate.
    """
    certificate = get_object_or_404(Certificate, certificate_number=certificate_id)
    
    # Check if user is authenticated and owns this certificate
    is_owner = request.user.is_authenticated and certificate.user == request.user
    
    context = {
        'certificate': certificate,
        'is_public': not is_owner,
    }
    return render(request, 'courses/certificate.html', context)


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


# Custom 404 view
def custom_page_not_found(request, exception):
    print("Custom 404 view called")  # Debug print
    print(f"Exception: {exception}")  # Debug print
    return render(request, '404.html', status=404)