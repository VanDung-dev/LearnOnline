from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    certificate_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Price for certificate. Set to 0 if certificate is free (when course price > 0) or if course is free."
    )
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Students must complete the course before this date to receive a certificate"
    )
    opening_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the course becomes available for enrollment"
    )
    closing_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the course enrollment closes"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Automatically set certificate_price to 0 if course price > 0
        # This ensures students don't have to pay twice for the course and certificate
        if self.price > 0:
            self.certificate_price = 0
            
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.slug})

    def is_certificate_free(self):
        """Check if certificate is free for students"""
        return self.price > 0 or self.certificate_price == 0


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    duration_days = models.PositiveIntegerField(
        default=7,
        help_text="Number of days students have to complete this module"
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="If checked, only students who purchased certificate can access this module"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} - {self.title}'
    
    def get_deadline(self, enrollment_date=None):
        """
        Calculate the deadline for this module based on the enrollment date and 
        the cumulative duration of preceding modules.
        If no enrollment_date is provided, use the course opening date.
        """
        # If no enrollment date provided, try to use course opening date
        if not enrollment_date:
            if not self.course.opening_date:
                return None
            start_date = self.course.opening_date
        else:
            start_date = enrollment_date
        
        # Get all modules in the course ordered by their order
        modules = Module.objects.filter(course=self.course).order_by('order')
        
        # Calculate cumulative days up to this module
        cumulative_days = 0
        for module in modules:
            cumulative_days += module.duration_days
            if module.id == self.id:
                break
        
        # Calculate deadline
        from django.utils import timezone
        from datetime import timedelta
        return start_date + timedelta(days=cumulative_days)


class Lesson(models.Model):
    LESSON_TYPES = (
        ('text', 'Text'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
    )

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=False)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPES, default='text')
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    is_locked = models.BooleanField(
        default=False,
        help_text="If checked, only students who purchased certificate can access this lesson"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    max_check = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of checks allowed for this quiz (0 for unlimited)"
    )

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness within the course (not just within the module)
            original_slug = self.slug
            counter = 1
            while Lesson.objects.filter(slug=self.slug, module__course=self.module.course).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.module.course.title} - {self.title}'


# Quiz models
class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.lesson:
            return f'Quiz for {self.lesson.title}'
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('essay', 'Essay Answer'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single')
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'Question: {self.text}'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'Answer: {self.text}'


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quiz_attempts')
    attempt_number = models.PositiveIntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'lesson', 'attempt_number')
        ordering = ['-started_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.lesson.title} - Attempt {self.attempt_number}'


class UserAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # For single choice questions, only one answer will be selected
    # For multiple choice questions, multiple answers can be selected
    selected_answers = models.ManyToManyField(Answer, blank=True)
    
    class Meta:
        unique_together = ('quiz_attempt', 'question')
    
    def __str__(self):
        return f'User answer for {self.question.text}'


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'
    
    def get_enrollment_date(self):
        """
        Get the enrollment date for this enrollment
        """
        return self.enrolled_at


class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f'{self.user.username} - {self.lesson.title} - Completed: {self.completed}'


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_number = models.CharField(max_length=50, unique=True)
    
    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'Certificate for {self.user.username} - {self.course.title}'
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate a unique certificate number
            import uuid
            self.certificate_number = str(uuid.uuid4()).replace('-', '').upper()[:12]
        super().save(*args, **kwargs)