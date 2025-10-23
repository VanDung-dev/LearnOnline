from django.db import models
from django.contrib.auth.models import User
from .managers import CustomUserManager


# Extend the User model manager
User.add_to_class('objects', CustomUserManager())


class Profile(models.Model):
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (INSTRUCTOR, 'Instructor'),
        (ADMIN, 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    website = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def is_student(self):
        return self.role == self.STUDENT
    
    def is_instructor(self):
        return self.role == self.INSTRUCTOR
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    objects = CustomUserManager()
