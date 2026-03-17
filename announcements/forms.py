from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from .models import Response
from .models import Profile
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Корпоративная почта")
    first_name = forms.CharField(max_length=30, required=True, label="Имя")
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email.endswith(settings.CORPORATE_EMAIL_DOMAIN):
            raise forms.ValidationError(f"Регистрация только по почте {settings.CORPORATE_EMAIL_DOMAIN}")
        return email

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['message', 'contact']          # ← добавили
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Почему хочешь в группу?'}),
            'contact': forms.TextInput(attrs={'placeholder': '@telegram или +7 (999) 123-45-67'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'autofocus': True}),
        label="Email"
    )