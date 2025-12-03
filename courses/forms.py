from django import forms
from .models import Course, Module, Lesson, Quiz, Question, Answer


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make description field not required in the form
        # (although it's still required in the model, we'll handle that in save method)
        self.fields['description'].required = False

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        certificate_price = cleaned_data.get('certificate_price')

        # If course price > 0, certificate price should be 0
        if price and price > 0:
            cleaned_data['certificate_price'] = 0

        return cleaned_data

    def save(self, commit=True):
        course = super().save(commit=False)
        
        # If no description provided, set it to empty string
        # This prevents issues with the required model field
        if not course.description:
            course.description = ''
            
        if commit:
            course.save()
        return course


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'duration_days', 'is_locked']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'lesson_type', 'content', 'video_url', 'video_file', 'video_duration', 'order', 'is_published', 'is_locked']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'lesson_type': forms.Select(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control','placeholder': 'https://www.youtube.com/watch?v=...'}),
            'video_file': forms.FileInput(attrs={'class': 'form-control'}),
            'video_duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
            'max_check': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text forvideo fields
        self.fields['video_url'].help_text = "Enter a YouTube or Vimeo URL"
        self.fields['video_file'].help_text = "Upload a video file (MP4, AVI, MOV, WMV, FLV, WEBM, MKV, M4V - max 500MB)"
        self.fields['video_duration'].help_text = "Enter video duration in HH:MM:SS format (optional)"
    
    def clean(self):
        cleaned_data = super().clean()
        lesson_type = cleaned_data.get('lesson_type')
        content = cleaned_data.get('content')
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')
        video_duration = cleaned_data.get('video_duration')
        
        # Validate based on lesson type
        if lesson_type == 'text' and not content:
            raise forms.ValidationError("Content is required for text lessons.")
        
        if lesson_type == 'video':
            # Either video_url or video_file must be provided, but not both
            if not video_url and not video_file:
                raise forms.ValidationError("Either Video URL or Video File is required for video lessons.")
            if video_url and video_file:
                raise forms.ValidationError("Please provide either Video URL or Video File, not both.")
            
            # Validate video URL format if provided
            if video_url:
                youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
                vimeo_pattern = r'(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(?:channels\/(?:\w+\/)?|groups\/(?:[^\/]*)\/videos\/|album\/(?:\d+)\/video\/|video\/|)(\d+)(?:[^\d]|$)'
                
                import re
                if not re.match(youtube_pattern, video_url) and not re.match(vimeo_pattern, video_url):
                    raise forms.ValidationError("Please enter a valid YouTube or Vimeo URL.")
            
            # Validate video duration format if provided
            if video_duration:
                duration_pattern = r'^([0-9]{1,2}):([0-5][0-9]):([0-5][0-9])$'
                import re
                if not re.match(duration_pattern, video_duration):
                    raise forms.ValidationError("Please enter video duration in HH:MM:SS format.")
        
        # For quiz type, no specific validation needed at creation time
        # Quiz configuration will be handled separately
        
        return cleaned_data


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }