from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^home/', views.IndexView.as_view(), name='index'),
    url(r'^institution/(?P<pk>[0-9]+)/$', views.InstitutionView.as_view(), name='institution'),
    url(r'^institutions/$', views.InstitutionListView.as_view(), name='institutions'),
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    url(r'^success/$', views.SuccessView.as_view(), name='success'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/home/'}, name='logout'),
    url(r'^contact/$', views.ContactView.as_view(), name='contact'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^account/$', views.AccountView.as_view(), name='account'),
    url(r'^account/company/(?P<pk>[0-9]+)/$', views.AccountCompanyView.as_view(), name='account_company'),
    url(r'^account/company/create/$', views.CompanyCreateView.as_view(), name='create_company'),
    url(r'^account/company/(?P<pk>[0-9]+)/institution/create/$', views.InstitutionCreateView.as_view(),
        name='create_institution'),
    url(r'^account/company/(?P<company_pk>[0-9]+)/institution/(?P<institution_pk>[0-9]+)/$',
        views.InstitutionPanelView.as_view(), name='institution_panel'),
    url(r'^account/company/(?P<company_pk>[0-9]+)/institution/(?P<institution_pk>[0-9]+)/crafts/edit/$',
        views.CraftsEditView.as_view(), name='crafts_edit'),
    url(r'^institution/(?P<pk>[0-9]+)/opinion/create/$', views.OpinionCreate.as_view(), name='opinion_create'),

]
