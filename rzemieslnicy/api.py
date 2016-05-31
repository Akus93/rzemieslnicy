from django.http import JsonResponse
from django.views import generic
from django.contrib.auth import authenticate, login, models

from rzemieslnicy.services import get_institutions, update_institution_rate, get_search_context, get_user_ad_info
from rzemieslnicy.forms import OpinionCreateForm, UserCreationForm
from rzemieslnicy.models import SearchHistory
from json import load as load_json


class SearchApi(generic.View):

    def get(self, request, *args, **kwargs):
        search = load_json(request.body)['search']  # request.GET['search']
        query_results = {'institutions': []}
        context = get_search_context(search)
        institutions = get_institutions(search, context)
        if institutions:
            if request.user.is_authenticated():
                try:
                    city = context['city'][0]
                except IndexError:
                    city = None
                try:
                    craft = context['craft'][0]
                except IndexError:
                    craft = None
                try:
                    province = context['province'][0]
                except IndexError:
                    province = None
                SearchHistory(user=request.user, city=city, craft=craft, province=province).save()
            for institution in institutions:
                query_results['institutions'].append(institution.as_dict())
        return JsonResponse(query_results)


class LoginApi(generic.View):

    def post(self, request, *args, **kwargs):
        json_data = load_json(request.body)
        username = json_data['username']  # request.POST['username']
        password = json_data['password']  # request.POST['password']
        response = {}
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                response['user'] = {}
                response['user']['username'] = user.username
                response['user']['first_name'] = user.first_name
                response['user']['last_name'] = user.last_name
                response['user']['ad_info'] = get_user_ad_info(user)
                return JsonResponse(response)
        return JsonResponse({'error': 'Błąd logowania'})


class OpinionCreateApi(generic.View):
    form_class = OpinionCreateForm

    def post(self, request, *args, **kwargs):
        json_data = load_json(request.body)
        institution_id = json_data['institution_id']  # request.POST.get('institution_id', '')
        try:
            user_pk = request.user.id
        except models.DoesNotExist:
            return JsonResponse({'error': 'Brak autoryzacji'})
        rating = json_data['rating']  # int(request.POST.get("rating", ""))
        form = self.form_class(json_data, institution=institution_id, user=user_pk, rating=rating)
        if form.is_valid():
            form.save()
            update_institution_rate(institution_id)
            return JsonResponse({'success': True})
        return JsonResponse({'errors': form.errors})


class SignupApi(generic.View):
    form_class = UserCreationForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(load_json(request.body))
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'errors': form.errors})
