from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.utils import timezone
from ..models import Category, Course, Lesson, Enrollment, Certificate, Quiz, Question, Answer
from ..forms import QuizForm


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


@login_required
def configure_quiz(request, lesson_id=None):
    if lesson_id:
        lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
        # Get or create quiz for this lesson
        quiz, created = Quiz.objects.get_or_create(lesson=lesson, defaults={'title': f'Quiz for {lesson.title}'})
    else:
        # Handle standalone quiz creation/configuration
        if request.method == 'POST' and 'quiz_id' in request.POST:
            quiz = get_object_or_404(Quiz, id=request.POST['quiz_id'])
        elif request.method == 'GET' and 'quiz_id' in request.GET:
            quiz = get_object_or_404(Quiz, id=request.GET['quiz_id'])
        else:
            quiz = Quiz()
        lesson = None

    # Handle form actions
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_question':
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

        elif action == 'edit_question':
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

        elif action == 'delete_question':
            # Delete question
            question_id = request.POST.get('question_id')
            question = get_object_or_404(Question, id=question_id, quiz=quiz)
            question.delete()
            messages.success(request, 'Question deleted successfully!')

        elif action is None:
            # Update quiz details
            form = QuizForm(request.POST, instance=quiz)
            if form.is_valid():
                form.save()
                messages.success(request, 'Quiz updated successfully!')
            else:
                messages.error(request, 'Error updating quiz!')

    # Handle question deletion via GET parameter (for backward compatibility)
    delete_question_id = request.GET.get('delete_question')
    if delete_question_id:
        question = get_object_or_404(Question, id=delete_question_id, quiz=quiz)
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        if lesson:
            return redirect('courses:configure_quiz', lesson_id=lesson.id)
        else:
            return redirect('courses:configure_quiz_standalone')

    # For GET requests or after POST actions, display the form
    form = QuizForm(instance=quiz)

    context = {
        'lesson': lesson,
        'quiz': quiz,
        'form': form,
    }
    return render(request, 'courses/configure_quiz.html', context)


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


# Custom 404 view
def custom_page_not_found(request, exception):
    print("Custom 404 view called")  # Debug print
    print(f"Exception: {exception}")  # Debug print
    return render(request, '404.html', status=404)