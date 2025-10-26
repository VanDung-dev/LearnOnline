from django import forms
from .models import Course, Module, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'short_description', 'description', 'category', 'price', 'certificate_price', 'thumbnail', 'is_active', 'opening_date', 'closing_date', 'expiration_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'opening_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'closing_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expiration_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        certificate_price = cleaned_data.get('certificate_price')

        # If course price > 0, certificate price should be 0
        if price and price > 0:
            cleaned_data['certificate_price'] = 0

        return cleaned_data


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'duration_days']
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