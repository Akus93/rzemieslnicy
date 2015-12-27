from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import password_validation

from django.core.mail import send_mail

from .models import Tradesman, Company, Institution, Area, City


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
    search = forms.CharField(max_length=100, required=True,
                             widget=forms.TextInput(attrs={'type': "search"}))


class ContactForm(forms.Form):
    subject = forms.CharField(required=True, max_length=100, label='Tytuł')
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': "materialize-textarea"}),
                              max_length=500, label='Wiadomość')
    email = forms.EmailField(required=True, max_length=150, label='Twój adres email')

    def send(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        from_email = self.cleaned_data['email']
        recipient_list = ['akus.quentin@gmail.com']
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)


class CompanyCreationForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ['name', 'krs', 'regon', 'address', 'postal_code', 'city', 'phone', 'email', 'site']

    def __init__(self, *args, **kwargs):
        self.tradesman = kwargs.pop('tradesman', None)
        super(CompanyCreationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        company = super(CompanyCreationForm, self).save(commit=False)
        company.tradesman = self.tradesman
        if commit:
            company.save()
        return company


class InstitutionCreationForm(forms.ModelForm):

    class Meta:
        model = Institution
        exclude = ['company']

    name = forms.CharField(max_length=128)
    area = forms.ModelChoiceField(queryset=Area.objects.all(), initial=0)
    address = forms.CharField(max_length=256)
    city = forms.ModelChoiceField(queryset=City.objects.all(), initial=0)
    postal_code = forms.CharField(max_length=6)
    phone = forms.CharField(max_length=15)
    email = forms.EmailField()
    site = forms.URLField(required=False)
    short_description = forms.CharField(max_length=100)
    long_description = forms.CharField(widget=forms.Textarea(attrs={'class': "materialize-textarea"}), max_length=500)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(InstitutionCreationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        institution = super(InstitutionCreationForm, self).save(commit=False)
        institution.company = Company.objects.get(pk=self.company)
        if commit:
            institution.save()
        return institution
