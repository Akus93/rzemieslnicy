from django.contrib import admin

from .models import *


class TradesmanAdmin(admin.ModelAdmin):
    list_display = ('user', 'NIP', )
    search_fields = ['NIP']
    list_per_page = 25


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tradesman', 'krs', 'regon', 'city')
    search_fields = ['name', 'krs', 'regon']
    list_filter = ['city']
    list_select_related = ['tradesman']
    list_per_page = 25


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'city', 'rate')
    search_fields = ['name', 'company__name', 'city__name']
    list_filter = ['city']
    list_select_related = ('company', 'city')
    list_per_page = 25


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province')
    list_filter = ['province']
    list_select_related = ['province']
    list_per_page = 25


class OpinionAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'rate', 'is_visible')
    list_filter = ['rate', 'is_visible']
    list_select_related = ['user', 'institution']
    list_editable = ['is_visible']
    list_per_page = 25


class PaidServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'time']
    list_per_page = 25


class InstitutionCraftAdmin(admin.ModelAdmin):
    list_display = ['institution', 'craft']
    search_fields = ['institiution', 'craft']
    list_filter = ['craft']
    list_select_related = ['institution', 'craft']
    list_per_page = 25


class ReportedOpinionAdmin(admin.ModelAdmin):
    list_display = ['opinion', 'user', 'reason', 'is_pending']
    list_filter = ['is_pending']
    list_select_related = ['opinion', 'user']
    list_editable = ['is_pending']
    list_per_page = 25


class ActiveServiceAdmin(admin.ModelAdmin):
    list_display = ['institution', 'paid_service', 'start_date', 'end_date']


admin.site.register(Tradesman, TradesmanAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Opinion, OpinionAdmin)
admin.site.register(PaidService, PaidServiceAdmin)
admin.site.register(InstitutionCraft, InstitutionCraftAdmin)
admin.site.register(ReportedOpinion, ReportedOpinionAdmin)
admin.site.register(ActiveService, ActiveServiceAdmin)

admin.site.register([Province, Craft, Area])
admin.site.register([Rating, SearchHistory])
