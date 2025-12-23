# Generated migration for database indexes
# Optimizes query performance for frequently accessed fields

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add database indexes for performance optimization.
    These indexes improve query speed for:
    - Course lookups by slug
    - Active course listings
    - Instructor course listings
    - Lesson lookups by slug
    - Enrollment queries
    - Progress tracking queries
    """

    dependencies = [
        ('courses', '0012_remove_lesson_max_attempts'),
    ]

    operations = [
        # Course indexes
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['slug'], name='course_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['is_active', '-created_at'], name='course_active_created_idx'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['instructor', '-created_at'], name='course_instructor_idx'),
        ),
        
        # Lesson indexes
        migrations.AddIndex(
            model_name='lesson',
            index=models.Index(fields=['slug'], name='lesson_slug_idx'),
        ),
        
        # Enrollment indexes
        migrations.AddIndex(
            model_name='enrollment',
            index=models.Index(fields=['user', 'course'], name='enrollment_user_course_idx'),
        ),
        
        # Progress indexes
        migrations.AddIndex(
            model_name='progress',
            index=models.Index(fields=['user', 'lesson'], name='progress_user_lesson_idx'),
        ),
        migrations.AddIndex(
            model_name='progress',
            index=models.Index(fields=['completed', 'user'], name='progress_completed_user_idx'),
        ),
    ]
