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
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    duration_days = models.PositiveIntegerField(
        default=7,
        help_text="Number of days students have to complete this module"
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
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness within the module
            original_slug = self.slug
            counter = 1
            while Lesson.objects.filter(module=self.module, slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.module.course.title} - {self.title}'


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