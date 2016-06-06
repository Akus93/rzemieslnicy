from django.db import models
from django.contrib.auth.models import User
from django.utils.timesince import timesince
from datetime import datetime
from django.utils.timezone import utc

from osm_field.fields import LatitudeField, LongitudeField, OSMField


class Tradesman(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Użytkownik')
    NIP = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Rzemieślnicy"
        verbose_name = 'rzemieślnika'

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return self.user.get_full_name()


class Company(models.Model):
    tradesman = models.ForeignKey(Tradesman, verbose_name='Rzemieślnik')
    name = models.CharField(max_length=255, unique=True, verbose_name='Nazwa')
    krs = models.CharField(max_length=10, unique=True)
    regon = models.CharField(max_length=14, unique=True, null=True)
    address = models.CharField(max_length=255, verbose_name='Adres')
    postal_code = models.CharField(max_length=6, verbose_name='Kod pocztowy')
    city = models.CharField(max_length=50, verbose_name='Miasto')
    phone = models.CharField(max_length=15, verbose_name='Telefon')
    email = models.EmailField(unique=True)
    site = models.URLField(null=True, verbose_name='Strona WWW')

    class Meta:
        verbose_name_plural = "Firmy"
        verbose_name = 'firmę'

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nazwa')

    class Meta:
        verbose_name_plural = 'Województwa'
        verbose_name = 'województwo'

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nazwa')
    province = models.ForeignKey(Province, verbose_name='Województwo')

    class Meta:
        verbose_name_plural = "Miasta"
        verbose_name = 'miasto'

    def __str__(self):
        return self.name


class Craft(models.Model):
    name = models.CharField(max_length=128, verbose_name='Nazwa')

    class Meta:
        verbose_name_plural = 'Specjalizacje'
        verbose_name = 'specjalizację'

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=45, verbose_name='Obszar')

    class Meta:
        verbose_name_plural = 'Obszary'
        verbose_name = 'obszar'

    def __str__(self):
        return self.name


class Institution(models.Model):
    company = models.ForeignKey(Company, verbose_name='Firma')
    name = models.CharField(max_length=128, verbose_name='Nazwa')
    area = models.ForeignKey(Area, verbose_name='Obszar')
    address = models.CharField(max_length=255, verbose_name='Adres')
    image = models.ImageField('Obrazek', upload_to='institution_images', blank=True)
    city = models.ForeignKey(City, verbose_name='Miasto')
    postal_code = models.CharField(max_length=6, verbose_name='Kod pocztowy')
    phone = models.CharField(max_length=15, verbose_name='Telefon')
    email = models.EmailField()
    site = models.URLField(null=True, verbose_name='Strona WWW')
    short_description = models.CharField(max_length=100, null=True, verbose_name='Krótki opis')
    long_description = models.TextField(max_length=500, verbose_name='Długi opis')
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=3.00, verbose_name='Ocena')
    location = OSMField(null=True, blank=True, verbose_name='Lokalizacja')
    location_lat = LatitudeField(null=True, blank=True, verbose_name='Szerokość geograficzna')
    location_lon = LongitudeField(null=True, blank=True, verbose_name='Długość geograficzna')
    is_visible = models.BooleanField(default=False, verbose_name='Czy widoczny?')

    class Meta:
        verbose_name_plural = 'Zakłady'
        verbose_name = 'zakład'

    def __str__(self):
        return self.name

    def is_awarded(self):
        if self.activeservice_set.filter(paid_service__name='Wyróżnienie'):
            return True
        return False

    def as_dict(self):
        opinions = []
        for opinion in self.opinion_set.all():
            opinions.append(opinion.as_dict())
        return {
            'company': self.company.name,
            'name': self.name,
            'area': self.area.name,
            'address': self.address,
            'city': self.city.name,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'email': self.email,
            'site': self.site,
            'short_description': self.short_description,
            'long_description': self.long_description,
            'rate': str(self.rate),
            'location': self.location,
            'location_lat': self.location_lat,
            'location_lon': self.location_lon,
            'opinions': opinions,
            'is_awarded': self.is_awarded()
        }


class InstitutionCraft(models.Model):
    institution = models.ForeignKey(Institution, verbose_name='Zakład')
    craft = models.ForeignKey(Craft, verbose_name='Specjalizacja')

    class Meta:
        verbose_name_plural = 'Specjalności zakładów'
        verbose_name = 'specjalność zakładu'


class Rating(models.Model):
    user = models.ForeignKey(User, verbose_name='Użytkownik')
    institution = models.ForeignKey(Institution, verbose_name='Zakład')
    value = models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Ocena')

    def __str__(self):
        return 'From: ' + self.user.get_full_name() + ' To: ' + self.institution.name

    class Meta:
        verbose_name_plural = 'Oceny'
        verbose_name = 'ocenę'


class Opinion(models.Model):
    user = models.ForeignKey(User, verbose_name='Użytkownik')
    institution = models.ForeignKey(Institution, verbose_name='Zakład')
    rate = models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Ocena')
    text = models.TextField(max_length=500, verbose_name='Treść opini')
    is_visible = models.BooleanField(default=True, verbose_name='Czy aktywna?')

    class Meta:
        verbose_name_plural = 'Opinie'
        verbose_name = 'opinię'

    def __str__(self):
        return '{} ocenił {}'.format(self.user.username, self.institution.name)

    def as_dict(self):
        if self.is_visible:
            return {
                'user': self.user.get_full_name() or self.user.username,
                'institution': self.institution.name,
                'rate': self.rate,
                'text': self.text
            }
        else:
            return None


class ReportedOpinion(models.Model):
    opinion = models.ForeignKey(Opinion, verbose_name='Opinia')
    user = models.ForeignKey(User, verbose_name='Użytkownik')
    reason = models.TextField(max_length=250, verbose_name='Powód')
    is_pending = models.BooleanField(default=True, verbose_name='Oczekujący')

    class Meta:
        verbose_name_plural = 'Zgłoszone opinie'
        verbose_name = 'zgłoszoną opinię'

    def __str__(self):
        return 'Zgłoszenie: {}'.format(self.opinion)


class PaidService(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nazwa')
    price = models.FloatField(verbose_name='Cena')
    description = models.TextField(max_length=150, verbose_name='Opis')
    time = models.IntegerField(verbose_name='Czas trwania')

    class Meta:
        verbose_name_plural = 'Płatne dodatki'
        verbose_name = 'płatny dodatek'

    def __str__(self):
        return self.name


class ActiveService(models.Model):
    institution = models.ForeignKey(Institution, verbose_name='Zakład')
    paid_service = models.ForeignKey(PaidService, verbose_name='Płatny dodatek')
    start_date = models.DateTimeField(verbose_name='Data aktywacji')
    end_date = models.DateTimeField(verbose_name='Data końca')

    class Meta:
        verbose_name_plural = 'Aktywne dodatki'
        verbose_name = 'aktywny dodatek'

    def __str__(self):
        return '{} aktywował {}'.format(self.institution, self.paid_service)

    def days_to_end(self):
        return timesince(datetime.now().replace(tzinfo=utc), self.end_date.replace(tzinfo=utc))


class SearchHistory(models.Model):
    user = models.ForeignKey(User, verbose_name='Użytkownik')
    city = models.CharField(max_length=32, null=True, verbose_name='Miasto')
    province = models.CharField(max_length=64, null=True, verbose_name='Województwo')
    craft = models.CharField(max_length=64, null=True, verbose_name='Specjalizacja')
    search_date = models.DateField(auto_now_add=True, verbose_name='Data wyszukiwania')

    class Meta:
        verbose_name_plural = 'Historie wyszukiwania'
        verbose_name = 'wyszukiwanie'
        ordering = ['-search_date']

    def __str__(self):
        return 'Wyszukiwanie użytkownika {}'.format(self.user.get_full_name() or self.user.username)

