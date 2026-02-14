 
from django import forms
from .models import Notification


class MarkEditForm(forms.Form):
    student_id = forms.IntegerField(widget=forms.HiddenInput())
    field_to_edit = forms.ChoiceField(
        choices=Notification.FIELD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    remark = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': 'Describe what needs to be changed...',
        })
    )