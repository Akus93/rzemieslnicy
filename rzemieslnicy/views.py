from django.views import generic
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Institution

from .services import get_institutions


class IndexView(generic.View):
    form_class = SearchForm
    template_name = 'rzemieslnicy/index.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            results = get_institutions(search)
            return render(request, 'rzemieslnicy/search_result.html', {'institutions': results})

        return render(request, self.template_name, {'form': form})


class InstitutionView(generic.DetailView):
    model = Institution
    template_name = 'rzemieslnicy/institution_view.html'
    context_object_name = 'institution'


class InstitutionList(generic.ListView):
    model = Institution
    queryset = Institution.objects.all()
    context_object_name = 'institutions'
    template_name = 'rzemieslnicy/institution_list.html'


class SuccessView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'rzemieslnicy/success.html'
    login_url = '/login/'


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






