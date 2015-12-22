from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import password_validation

from .models import Tradesman


class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    username = forms.CharField(label="Username", max_length=30, required=True)
    password1 = forms.CharField(label="Password", required=True,
        widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", required=True,
        widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="First name")
    last_name = forms.CharField(max_length=30, required=True, label="Last name")

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "email", "first_name", "last_name"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class TradesmanCreationForm(UserCreationForm):

    class Meta:
        model = Tradesman
        fields = ["username", "password1", "password2", "email", "first_name", "last_name", "NIP"]

    def save(self, commit=True):
        user = User.objects.create_user(self.cleaned_data['username'])
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        tradesman = Tradesman(user=user, NIP=self.cleaned_data['NIP'])
        if commit:
            tradesman.save()
        return tradesman


class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=True)


