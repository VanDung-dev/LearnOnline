from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from apps.courses.models import Course, Enrollment, Progress, Lesson
from apps.payments.models import Payment

def get_student_progress(user):
    """
    Returns progress for each course the student is enrolled in.
    """
    enrollments = Enrollment.objects.filter(user=user).select_related('course')
    data = []

    for enrollment in enrollments:
        course = enrollment.course
        # Calculate progress using Progress model
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = Progress.objects.filter(
            user=user, 
            lesson__module__course=course, 
            completed=True
        ).count()
        
        progress_percent = 0
        if total_lessons > 0:
            progress_percent = int((completed_lessons / total_lessons) * 100)
            
        data.append({
            'course_title': course.title,
            'progress_percent': progress_percent,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons
        })
    return data

def get_instructor_stats(user):
    """
    Returns statistics for the instructor.
    """
    courses = Course.objects.filter(instructor=user)
    total_students = Enrollment.objects.filter(course__in=courses).count()
    
    # Calculate Revenue (assuming Payment has 'amount' and 'status')
    # If Payment model isn't fully set up, we handle gracefully.
    try:
        total_revenue = Payment.objects.filter(
            course__in=courses, 
            status='succeeded' 
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    except Exception:
        total_revenue = 0

    # Monthly enrollment trend (for Chart)
    # Group enrollments by month
    monthly_enrollments = list(Enrollment.objects.filter(course__in=courses)
        .annotate(month=TruncMonth('enrolled_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    return {
        'total_students': total_students,
        'total_courses': courses.count(),
        'total_revenue': total_revenue,
        'monthly_enrollments': monthly_enrollments
    }
