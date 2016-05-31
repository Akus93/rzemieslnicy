from operator import and_
from django.db.models import Q
from functools import reduce

from .models import Institution, City, Province, Craft, InstitutionCraft, Opinion, SearchHistory
from django.db.models import Avg, Count


def pl_to_en(word):
    return word.translate(str.maketrans("ąćęłńóśżźĄĆĘŁŃÓŚŻŹ", "acelnoszzACELNOSZZ"))


def get_search_context(search):
    words = search.split()
    context = {
        'city': [],
        'province': [],
        'craft': [],
        'name': [],
    }
    for word in words:
        word = pl_to_en(word)
        if City.objects.filter(name=word.capitalize()).exists():
            context['city'].append(word.capitalize())
        elif Province.objects.filter(name__startswith=word[:5].capitalize()).exists():
            context['province'].append(word[:5].capitalize())
        elif Craft.objects.filter(name=word.capitalize()).exists():
            context['craft'].append(word.capitalize())
        elif Institution.objects.filter(name__icontains=word).exists():
            context['name'].append(word)
    return context


def get_institutions(search, context=False):
    if not context:
        context = get_search_context(search)
    results = None
    if len(context['city']):
        results = Institution.objects.filter(city__name__in=context['city'])
    if len(context['province']):
        if results is None:
            query = reduce(and_, (Q(city__province__name__startswith=x) for x in context['province']))
            results = Institution.objects.filter(query)
    if len(context['craft']):
        if results is not None:
            results = results.filter(institutioncraft__craft__name__in=context['craft'])
        else:
            results = Institution.objects.filter(institutioncraft__craft__name__in=context['craft'])
    if len(context['name']):
        query = reduce(and_, (Q(name__icontains=x) for x in context['name']))
        if results is None:
            results = Institution.objects.filter(query)
        else:
            results = results.filter(query)
    if results:
        results = results.select_related('company', 'area', 'city', 'city__province', ).order_by('-rate')
    return results


def remove_all_crafts(institution):
    old_crafts = [craft for craft in InstitutionCraft.objects.filter(institution=institution)]
    for old_craft in old_crafts:
        old_craft.delete()


def update_crafts(institution, crafts):
    remove_all_crafts(institution)
    institution_obj = Institution.objects.get(pk=institution)
    for craft in crafts:
        craft_obj = Craft.objects.get(pk=craft)
        new_craft = InstitutionCraft(institution=institution_obj, craft=craft_obj)
        new_craft.save()


# TODO gdy admin ukrywa opinie wywolanie tej funkcji
def update_institution_rate(institution_pk):
    institution = Institution.objects.get(id=institution_pk)
    new_rate = Opinion.objects.filter(institution=institution).filter(is_visible=True).aggregate(Avg('rate')).get('rate__avg')
    institution.rate = new_rate
    institution.save()


def get_user_ad_info(user):
    if SearchHistory.objects.filter(user=user, city__isnull=False).exists():
        top_city = SearchHistory.objects.filter(user=user).exclude(city__isnull=True).values('city') \
                                        .annotate(city_count=Count('city')).order_by('-city_count')[0]['city']
    else:
        top_city = False
    if SearchHistory.objects.filter(user=user, province__isnull=False).exists():
        top_province = SearchHistory.objects.filter(user=user).exclude(province__isnull=True).values('province') \
                                .annotate(province_count=Count('province')).order_by('-province_count')[0]['province']
    else:
        top_province = False
    if SearchHistory.objects.filter(user=user, craft__isnull=False).exists():
        top_craft = SearchHistory.objects.filter(user=user).exclude(craft__isnull=True).values('craft') \
            .annotate(craft_count=Count('craft')).order_by('-craft_count')[0]['craft']
    else:
        top_craft = False

    return dict(top_city=top_city, top_craft=top_craft, top_province=top_province)






