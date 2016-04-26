# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-26 08:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import osm_field.fields
import osm_field.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('krs', models.CharField(max_length=10, unique=True)),
                ('regon', models.CharField(max_length=14, null=True, unique=True)),
                ('address', models.CharField(max_length=256)),
                ('postal_code', models.CharField(max_length=6)),
                ('city', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('site', models.URLField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='Craft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('address', models.CharField(max_length=256)),
                ('postal_code', models.CharField(max_length=6)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('site', models.URLField(null=True)),
                ('short_description', models.CharField(max_length=100, null=True)),
                ('long_description', models.TextField(max_length=500)),
                ('rate', models.DecimalField(decimal_places=2, default=3.0, max_digits=3)),
                ('location', osm_field.fields.OSMField(lat_field='location_lat', lon_field='location_lon', null=True)),
                ('location_lat', osm_field.fields.LatitudeField(null=True, validators=[osm_field.validators.validate_latitude])),
                ('location_lon', osm_field.fields.LongitudeField(null=True, validators=[osm_field.validators.validate_longitude])),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Area')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.City')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Company')),
            ],
        ),
        migrations.CreateModel(
            name='InstitutionCraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('craft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Craft')),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Institution')),
            ],
        ),
        migrations.CreateModel(
            name='Opinion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('text', models.TextField(max_length=500)),
                ('is_visible', models.BooleanField(default=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Institution')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaidService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.FloatField()),
                ('description', models.TextField(max_length=150)),
                ('time', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Institution')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReportedOpinion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(max_length=250)),
                ('is_pending', models.BooleanField(default=True)),
                ('opinion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Opinion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tradesman',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NIP', models.CharField(max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Tradesmen',
            },
        ),
        migrations.AddField(
            model_name='company',
            name='tradesman',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Tradesman'),
        ),
        migrations.AddField(
            model_name='city',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Province'),
        ),
        migrations.AddField(
            model_name='activeservice',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.Institution'),
        ),
        migrations.AddField(
            model_name='activeservice',
            name='paid_service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rzemieslnicy.PaidService'),
        ),
    ]
