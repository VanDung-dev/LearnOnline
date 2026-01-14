from django import forms
from .models import Discussion, Reply

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Discussion Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control tinymce-editor', 'rows': 5, 'placeholder': 'What\'s on your mind?'}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write a reply...'}),
        }
