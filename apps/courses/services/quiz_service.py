"""
Quiz Service - Business logic for Quiz grading and attempts

This layer contains all business logic for Quiz management,
separated from views for better testability and reusability.
"""
from typing import Dict, Any, List
from django.contrib.auth.models import User
from django.utils import timezone

from ..models import Lesson, Quiz, Question, Answer, QuizAttempt, UserAnswer


def grade_quiz_attempt(
    quiz_attempt: QuizAttempt,
    answers: Dict[int, List[int]]
) -> Dict[str, Any]:
    """Grade a quiz attempt with user answers"""
    quiz = quiz_attempt.lesson.quiz
    total_points = 0
    earned_points = 0
    results = []

    for question in quiz.questions.all():
        total_points += question.points

        user_answer_ids = answers.get(question.id, [])
        correct_answer_ids = list(question.answers.filter(is_correct=True).values_list('id', flat=True))

        is_correct = sorted(user_answer_ids) == sorted(correct_answer_ids)

        if is_correct:
            earned_points += question.points

        results.append({
            'question_id': question.id,
            'correct': is_correct,
            'points': question.points,
            'earned': question.points if is_correct else 0
        })

    score = (earned_points / total_points) * 100 if total_points > 0 else 0

    quiz_attempt.score = score
    quiz_attempt.completed_at = timezone.now()
    quiz_attempt.save()

    return {
        'score': round(score, 2),
        'total_points': total_points,
        'earned_points': earned_points,
        'results': results
    }


def create_quiz_attempt(user: User, lesson: Lesson) -> QuizAttempt:
    """Create a new quiz attempt for user"""
    last_attempt = QuizAttempt.objects.filter(user=user, lesson=lesson).order_by('-attempt_number').first()
    attempt_number = last_attempt.attempt_number + 1 if last_attempt else 1

    if lesson.max_check > 0 and attempt_number > lesson.max_check:
        raise ValueError("Maximum number of attempts reached")

    return QuizAttempt.objects.create(
        user=user,
        lesson=lesson,
        attempt_number=attempt_number
    )


def save_user_answers(
    quiz_attempt: QuizAttempt,
    question: Question,
    answer_ids: List[int]
) -> UserAnswer:
    """Save user answers for a question"""
    user_answer, _ = UserAnswer.objects.get_or_create(
        quiz_attempt=quiz_attempt,
        question=question
    )

    user_answer.selected_answers.set(answer_ids)
    user_answer.save()

    return user_answer


def get_quiz_results(quiz_attempt: QuizAttempt) -> Dict[str, Any]:
    """Get formatted results for a quiz attempt"""
    return {
        'id': quiz_attempt.id,
        'score': quiz_attempt.score,
        'attempt_number': quiz_attempt.attempt_number,
        'started_at': quiz_attempt.started_at,
        'completed_at': quiz_attempt.completed_at,
    }
