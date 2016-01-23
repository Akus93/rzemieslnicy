from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import password_validation

from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import Tradesman, Company, Institution, Area, City, Opinion, ReportedOpinion, ActiveService, PaidService


class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    username = forms.CharField(max_length=30, required=True)
    password1 = forms.CharField(required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['password1'].label = 'Hasło'
        self.fields['password2'].label = 'Powtórz hasło'
        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['first_name'].label = 'Imię'
        self.fields['last_name'].label = 'Nazwisko'

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

    def __init__(self, *args, **kwargs):
        super(TradesmanCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['password1'].label = 'Hasło'
        self.fields['password2'].label = 'Powtórz hasło'
        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['first_name'].label = 'Imię'
        self.fields['last_name'].label = 'Nazwisko'

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
        self.fields['name'].label = 'Nazwa'
        self.fields['address'].label = 'Adres'
        self.fields['postal_code'].label = 'Kod pocztowy'
        self.fields['city'].label = 'Miasto'
        self.fields['phone'].label = 'Telefon'
        self.fields['site'].label = 'Strona WWW'

    def save(self, commit=True):
        company = super(CompanyCreationForm, self).save(commit=False)
        company.tradesman = self.tradesman
        if commit:
            company.save()
        return company


class InstitutionCreationForm(forms.ModelForm):

    class Meta:
        model = Institution
        exclude = ['company', 'rate', 'location', 'location_lat', 'location_lon']

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
        self.location_lon = None
        self.location_lat = None
        self.location = None
        super(InstitutionCreationForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nazwa'
        self.fields['address'].label = 'Adres'
        self.fields['postal_code'].label = 'Kod pocztowy'
        self.fields['city'].label = 'Miasto'
        self.fields['phone'].label = 'Telefon'
        self.fields['site'].label = 'Strona WWW'
        self.fields['short_description'].label = 'Krótki opis'
        self.fields['long_description'].label = 'Długi opis'
        self.fields['area'].label = 'Zasięg'

    def save(self, commit=True):
        institution = super(InstitutionCreationForm, self).save(commit=False)
        institution.company = Company.objects.get(pk=self.company)
        institution.rate = 3.00
        if commit:
            institution.save()
        return institution


class OpinionCreateForm(forms.ModelForm):

    class Meta:
        model = Opinion
        exclude = ['user', 'institution', 'is_visible', 'is_positive', 'rate']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.institution = kwargs.pop('institution', None)
        self.rate = kwargs.pop('rating', None)
        super(OpinionCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        opinion = super(OpinionCreateForm, self).save(commit=False)
        opinion.user = User.objects.get(pk=self.user)
        opinion.rate = self.rate
        opinion.institution = Institution.objects.get(pk=self.institution)
        if commit:
            opinion.save()
        return opinion


class OpinionReportForm(forms.ModelForm):

    class Meta:
        model = ReportedOpinion
        fields = ['reason']

    reason = forms.CharField(widget=forms.Textarea(attrs={'class': "materialize-textarea"}), max_length=200)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.opinion = kwargs.pop('opinion', None)
        super(OpinionReportForm, self).__init__(*args, **kwargs)
        self.fields['reason'].label = 'Powód'

    def save(self, commit=True):
        reported_opinion = super(OpinionReportForm, self).save(commit=False)
        reported_opinion.user = User.objects.get(pk=self.user)
        reported_opinion.opinion = Opinion.objects.get(pk=self.opinion)
        if commit:
            reported_opinion.save()
        return reported_opinion


class ServiceAddForm(forms.ModelForm):

    paid_service = forms.ModelChoiceField(queryset=PaidService.objects.all(), initial=0)

    class Meta:
        model = ActiveService
        fields = ['paid_service']

    def __init__(self, *args, **kwargs):
        self.institution = kwargs.pop('institution', None)
        self.service = kwargs.pop('service', None)
        super(ServiceAddForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        service = ActiveService()
        service.institution = Institution.objects.get(pk=self.institution)
        service.paid_service = PaidService.objects.get(pk=self.service)
        service.start_date = datetime.now()
        service.end_date = service.start_date + timedelta(days=service.paid_service.time)
        if commit:
            service.save()
        return service


class MapAddForm(forms.ModelForm):

    class Meta:
        fields = ('location', 'location_lat', 'location_lon', )
        model = Institution
        widgets = {'location_lat': forms.HiddenInput(),
                   'location_lon': forms.HiddenInput()}








