from django.db import models
from django.contrib.auth.models import User


class Tradesman(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    NIP = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Tradesmen"

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class Company(models.Model):
    tradesman = models.ForeignKey(Tradesman)
    name = models.CharField(max_length=256, unique=True)
    krs = models.CharField(max_length=10, unique=True)
    regon = models.CharField(max_length=14, unique=True, null=True)
    address = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=6)
    city = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    site = models.URLField(null=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50)
    province = models.ForeignKey(Province)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class Craft(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name


class Institution(models.Model):
    company = models.ForeignKey(Company)
    name = models.CharField(max_length=128)
    area = models.ForeignKey(Area)
    address = models.CharField(max_length=256)
    city = models.ForeignKey(City)
    postal_code = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    site = models.URLField(null=True)
    short_description = models.CharField(max_length=100, null=True)
    long_description = models.TextField(max_length=500)

    def __str__(self):
        return self.name


class InstitutionCraft(models.Model):
    institution = models.ForeignKey(Institution)
    craft = models.ForeignKey(Craft)


class Rating(models.Model):
    user = models.ForeignKey(User)
    institution = models.ForeignKey(Institution)
    value = models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])

    def __str__(self):
        return 'From: ' + self.user.get_full_name() + ' To: ' + self.institution.name


class Opinion(models.Model):
    user = models.ForeignKey(User)
    institution = models.ForeignKey(Institution)
    text = models.TextField(max_length=500)
    is_positive = models.BooleanField()
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.text


class ReportedOpinion(models.Model):
    opinion = models.ForeignKey(Opinion)
    user = models.ForeignKey(User)
    reason = models.TextField(max_length=250)
    is_pending = models.BooleanField(default=True)

    def __str__(self):
        return self.opinion.text


class PaidService(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    description = models.TextField(max_length=150)
    time = models.DurationField()

    def __str__(self):
        return self.name


class ActiveService(models.Model):
    tradesman = models.ForeignKey(Tradesman)
    paid_service = models.ForeignKey(PaidService)
    start_date = models.DateTimeField()
    end_time = models.DateTimeField()
