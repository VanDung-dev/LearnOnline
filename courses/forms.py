from django import forms
from .models import Course, Module, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'short_description', 'description', 'category', 'price', 'thumbnail', 'is_active', 'opening_date', 'closing_date', 'expiration_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'opening_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'closing_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expiration_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'lesson_type', 'content', 'video_url', 'order', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }