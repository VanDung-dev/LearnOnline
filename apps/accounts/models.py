import os

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from apps.organization.models import School


# Extend the User model manager
User.add_to_class('objects', CustomUserManager())


class Profile(models.Model):
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    SCHOOL_ADMIN = 'school_admin'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (INSTRUCTOR, 'Instructor'),
        (SCHOOL_ADMIN, 'School Admin'),
        (ADMIN, 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    website = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    employee_id = models.CharField(max_length=50, blank=True, help_text='Staff/Instructor ID within the school')
    
    def clean(self):
        # Validate profile picture
        if self.profile_picture:
            # Check file size (limit to 5MB)
            if self.profile_picture.size > 5242880:  # 5MB in bytes
                raise ValidationError(_('Profile picture size must be less than 5MB.'))
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(self.profile_picture.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(_('Unsupported file extension for profile picture. Allowed extensions are: %s' % ', '.join(valid_extensions)))

    def save(self, *args, **kwargs):
        # Clean the instance before saving
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def is_student(self):
        return self.role == self.STUDENT
    
    def is_instructor(self):
        return self.role == self.INSTRUCTOR
    
    def is_school_admin(self):
        return self.role == self.SCHOOL_ADMIN
    
    def is_admin(self):
        return self.role == self.ADMIN
