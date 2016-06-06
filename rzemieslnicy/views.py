from uuid import uuid4
from base64 import b64decode

from django.core.files.base import ContentFile
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from rzemieslnicy.forms import *
from rzemieslnicy.models import Institution, Company, Craft
from rzemieslnicy.services import get_institutions, update_crafts, update_institution_rate


class IndexView(generic.View):
    form_class = SearchForm
    template_name = 'rzemieslnicy/index.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        premium = Institution.objects.filter(activeservice__paid_service__name='Wyróżnienie')
        return render(request, self.template_name, {'form': form, 'institutions': premium})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            results = get_institutions(search)
            return render(request, 'rzemieslnicy/index.html', {'institutions': results})
        return render(request, self.template_name, {'form': form})


class InstitutionView(generic.DetailView):
    model = Institution
    template_name = 'rzemieslnicy/institution_view.html'
    context_object_name = 'institution'


class SuccessView(generic.TemplateView):
    template_name = 'rzemieslnicy/success.html'


class SignupView(generic.View):
    user_form_class = UserCreationForm
    tradesman_form_class = TradesmanCreationForm
    template_name = 'rzemieslnicy/signup_form.html'

    def get(self, request, *args, **kwargs):
        user_form = self.user_form_class()
        tradesman_form = self.tradesman_form_class()
        return render(request, self.template_name, {'user_form': user_form, 'tradesman_form': tradesman_form})

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class()
        tradesman_form = self.tradesman_form_class()

        if 'user_form' in request.POST:
            user_form = self.user_form_class(request.POST)
            if user_form.is_valid():
                user_form.save()
                return HttpResponseRedirect('/success/')
        elif 'tradesman_form' in request.POST:
            tradesman_form = self.tradesman_form_class(request.POST)
            if tradesman_form.is_valid():
                tradesman_form.save()
                return HttpResponseRedirect('/success/')
        return render_to_response(self.template_name, {'user_form': user_form, 'tradesman_form': tradesman_form}, context_instance=RequestContext(request))


class ContactView(generic.View):
    form_class = ContactForm
    template_name = 'rzemieslnicy/contact.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.send()
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class AboutView(generic.TemplateView):
    template_name = 'rzemieslnicy/about.html'


class AccountView(LoginRequiredMixin, generic.View):
    template_name = 'rzemieslnicy/account.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        change_password_form = ChangePasswordForm(request.user)
        return render(request, self.template_name, {'change_password_form': change_password_form})


class AccountCompanyView(generic.DetailView):
    model = Company
    template_name = 'rzemieslnicy/company_view.html'
    context_object_name = 'company'


class CompanyCreateView(generic.View):
    form_class = CompanyCreationForm
    template_name = 'rzemieslnicy/company_create.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, tradesman=request.user.tradesman)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/account/')
        return render(request, self.template_name, {'form': form})


class InstitutionCreateView(generic.View):
    form_class = InstitutionCreationForm
    template_name = 'rzemieslnicy/institution_create.html'

    def is_owner(self, request):
        pk = self.kwargs['pk']
        indexes = [company.id for company in request.user.tradesman.company_set.all()]
        if int(pk) in indexes:
            return True
        return False

    def get(self, request, *args, **kwargs):
        if self.is_owner(request):
            form = self.form_class()
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/account/')

    def post(self, request, *args, **kwargs):
        if self.is_owner(request):
            img64 = request.POST['imagebase64'].split(',')[1]
            request.FILES['image'] = ContentFile(b64decode(img64), '{}.png'.format(uuid4()))
            form = self.form_class(request.POST, request.FILES, company=self.kwargs['pk'])
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/account/')
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/account/')


class AccountInstitutionView(generic.View):
    map_form_class = MapAddForm
    template_name = 'rzemieslnicy/institution_panel.html'

    def is_owner(self, request):
        company_pk = int(self.kwargs['company_pk'])
        companies = request.user.tradesman.company_set.all()
        companies_id = [company.id for company in companies]
        institution_pk = int(self.kwargs['institution_pk'])
        if company_pk in companies_id:
            company = Company.objects.get(pk=company_pk)
            instituitons_id = [institution.id for institution in company.institution_set.all()]
            if institution_pk in instituitons_id:
                return True
        return False

    def get(self, request, *args, **kwargs):
        if self.is_owner(request):
            pk = int(self.kwargs['institution_pk'])
            instituiton = Institution.objects.get(pk=pk)
            map_form = self.map_form_class()
            return render(request, self.template_name, {'institution': instituiton, 'map_form': map_form})
        return HttpResponseRedirect('/account/')


class CraftsEditView(generic.View):
    template_name = 'rzemieslnicy/crafts_edit.html'

    def is_owner(self, request):
        company_pk = int(self.kwargs['company_pk'])
        companies = request.user.tradesman.company_set.all()
        companies_id = [company.id for company in companies]
        institution_pk = int(self.kwargs['institution_pk'])
        if company_pk in companies_id:
            company = Company.objects.get(pk=company_pk)
            instituitons_id = [institution.id for institution in company.institution_set.all()]
            if institution_pk in instituitons_id:
                return True
        return False

    def get(self, request, *args, **kwargs):
        if self.is_owner(request):
            crafts = Craft.objects.all().order_by('name')
            institution = Institution.objects.get(pk=int(self.kwargs['institution_pk']))
            checked = [ins_craft.craft for ins_craft in institution.institutioncraft_set.all()]
            return render(request, self.template_name, {'crafts': crafts, 'checked': checked})
        return HttpResponseRedirect('/account/')

    def post(self, request, *args, **kwargs):
        if self.is_owner(request):
            crafts = list(map(int, request.POST.getlist('crafts')))
            all_crafts = [craft.id for craft in Craft.objects.all()]
            if set(crafts).issubset(set(all_crafts)):
                update_crafts(self.kwargs['institution_pk'], crafts)
        return HttpResponseRedirect('/account/')


class OpinionCreateView(generic.View):
    template_name = 'rzemieslnicy/opinion_create.html'
    form_class = OpinionCreateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        institution_pk = self.kwargs['pk']
        user_pk = request.user.id
        rating = int(request.POST.get("rating", ""))
        form = self.form_class(request.POST, institution=institution_pk, user=user_pk, rating=rating)
        if form.is_valid():
            form.save()
            update_institution_rate(institution_pk)
            return HttpResponseRedirect('/institution/%s' % institution_pk)
        return render(request, self.template_name, {'form': form})


class OpinionReportView(generic.View):
    template_name = 'rzemieslnicy/opinion_report.html'
    form_class = OpinionReportForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        opinion_pk = self.kwargs['opinion_pk']
        opinion = Opinion.objects.get(id=opinion_pk)
        return render(request, self.template_name, {'form': form, 'opinion': opinion})

    def post(self, request, *args, **kwargs):
        institution_pk = self.kwargs['institution_pk']
        opinion_pk = self.kwargs['opinion_pk']
        user_pk = request.user.id
        form = self.form_class(request.POST, opinion=opinion_pk, user=user_pk)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/institution/%s' % institution_pk)
        return render(request, self.template_name, {'form': form})


class ServiceAddView(generic.View):
    template_name = 'rzemieslnicy/service_add.html'
    form_class = ServiceAddForm

    def is_owner(self, request):
        company_pk = int(self.kwargs['company_pk'])
        companies = request.user.tradesman.company_set.all()
        companies_id = [company.id for company in companies]
        institution_pk = int(self.kwargs['institution_pk'])
        if company_pk in companies_id:
            company = Company.objects.get(pk=company_pk)
            instituitons_id = [institution.id for institution in company.institution_set.all()]
            if institution_pk in instituitons_id:
                return True
        return False

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        institution_pk = self.kwargs['institution_pk']
        service_id = int(request.POST.get('paid_service'))
        form = self.form_class(request.POST, institution=institution_pk, service=service_id)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/institution/%s' % institution_pk)
        return render(request, self.template_name, {'form': form})


class MapAddView(generic.View):
    form_class = MapAddForm
    template_name = 'rzemieslnicy/add_map.html'

    def is_owner(self, request):
        company_pk = int(self.kwargs['company_pk'])
        companies = request.user.tradesman.company_set.all()
        companies_id = [company.id for company in companies]
        institution_pk = int(self.kwargs['institution_pk'])
        if company_pk in companies_id:
            company = Company.objects.get(pk=company_pk)
            instituitons_id = [institution.id for institution in company.institution_set.all()]
            if institution_pk in instituitons_id:
                return True
        return False

    def get(self, request, *args, **kwargs):
        if self.is_owner(request):
            form = self.form_class()
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/account')

    def post(self, request, *args, **kwargs):
        if self.is_owner(request):
            institution_pk = self.kwargs['institution_pk']
            institution = Institution.objects.get(id=institution_pk)
            form = self.form_class(request.POST)
            if form.is_valid():
                institution.location = form.cleaned_data['location']
                institution.location_lat = form.cleaned_data['location_lat']
                institution.location_lon = form.cleaned_data['location_lon']
                institution.save()
                return HttpResponseRedirect('/institution/%s' % institution_pk)
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/account')


class InstitutionUpdateView(generic.UpdateView):
    model = Institution
    fields = ['phone', 'email', 'site', 'area', 'short_description', 'long_description']
    template_name = 'rzemieslnicy/institution_update.html'
    success_url = '/account'

    def get_object(self, queryset=None):
        institution = super().get_object()
        if not institution.company.tradesman.user == self.request.user:
            raise Http404
        return institution


class InstitutionDeleteView(generic.DeleteView):
    model = Institution

    def get_object(self, queryset=None):
        institution = super().get_object()
        if not institution.company.tradesman.user == self.request.user:
            raise Http404
        return institution


class CompanyUpdateView(generic.UpdateView):
    model = Company
    fields = ['phone', 'email', 'site']
    template_name = 'rzemieslnicy/company_update.html'
    success_url = '/account'

    def get_object(self, queryset=None):
        company = super().get_object()
        if not company.tradesman.user == self.request.user:
            raise Http404
        return company


class CompanyDeleteView(generic.DeleteView):
    model = Company

    def get_object(self, queryset=None):
        company = super().get_object()
        if not company.tradesman.user == self.request.user:
            raise Http404
        return company


class ChangePasswordView(LoginRequiredMixin, generic.View):
    login_url = '/login'
    form_class = ChangePasswordForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login/')
        return render(request, 'rzemieslnicy/account.html', {'change_password_form': form, 'error_change_password': True})


class UserUpdateView(generic.UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'rzemieslnicy/user_update.html'
    success_url = '/account'

    def get_object(self, queryset=None):
        user = super().get_object()
        if not user == self.request.user:
            raise Http404
        return user








