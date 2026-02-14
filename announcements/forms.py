from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'category', 'priority',
            'visibility', 'is_pinned', 'attachment', 'expires_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Announcement title...',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 5,
                'placeholder': 'Write your announcement here...',
            }),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
            'visibility': forms.Select(attrs={'class': 'form-input'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'attachment': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
            }),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Max 5MB
            if attachment.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Attachment size must be under 5MB.')

            # Allowed extensions
            import os
            ext = os.path.splitext(attachment.name)[1].lower()
            allowed = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            if ext not in allowed:
                raise forms.ValidationError(f'File type {ext} not allowed. Allowed: {", ".join(allowed)}')

        return attachment