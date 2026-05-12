from django import forms
from .models import ScreenTimeLog


class ScreenTimeLogForm(forms.ModelForm):
    DURATION_UNIT_CHOICES = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
    ]

    duration_value = forms.DecimalField(
        label='Duration',
        min_value=0.1,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 60 or 1.5',
            'step': '0.1',
        })
    )
    duration_unit = forms.ChoiceField(
        choices=DURATION_UNIT_CHOICES,
        initial='minutes',
        widget=forms.Select(attrs={
            'class': 'form-input',
        })
    )

    class Meta:
        model = ScreenTimeLog
        fields = ['app_name', 'category', 'date', 'notes']
        widgets = {
            'app_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. YouTube, Instagram, VS Code...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Optional notes...',
                'rows': 3,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data.get('duration_value')
        unit = cleaned_data.get('duration_unit')
        if value is None or unit is None:
            return cleaned_data

        if unit == 'hours':
            cleaned_data['duration_minutes'] = int(round(float(value) * 60))
        else:
            cleaned_data['duration_minutes'] = int(round(float(value)))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.duration_minutes = self.cleaned_data.get('duration_minutes', 0)
        if commit:
            instance.save()
        return instance