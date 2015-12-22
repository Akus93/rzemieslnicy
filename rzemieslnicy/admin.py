from django.contrib import admin

from .models import *


admin.site.register([Tradesman, Company, Province, City, Craft, Area, Institution, InstitutionCraft])
admin.site.register([Rating, Opinion, ReportedOpinion, PaidService, ActiveService])
