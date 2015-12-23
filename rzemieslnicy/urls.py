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

    url(r'^account/companies/$', views.CompanyListView.as_view(), name='account_companies'),
    url(r'^account/company/(?P<pk>[0-9]+)/$', views.AccountCompanyView.as_view(), name='account_company'),
]
