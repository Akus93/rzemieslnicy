from .models import Institution, City, Province, Craft, InstitutionCraft
from functools import reduce
from django.db.models import Q


def get_search_context(search):
    words = search.split()
    context = {
        'city': [],
        'province': [],
        'craft': [],
        'name': [],
    }
    for word in words:
        if City.objects.filter(name=word.capitalize()).exists():
            context['city'].append(word.capitalize())
        elif Province.objects.filter(name=word.capitalize()).exists():
            context['province'].append(word.capitalize())
        elif Craft.objects.filter(name=word).exists():
            context['craft'].append(word)
        elif Institution.objects.filter(name=word).exists():
            context['name'].append(word)
    return context


def get_q_queries(search):
    context = get_search_context(search)
    queries = {
        'cities': [],
        'provincies': [],
        'crafts': [],
        'names': [],
    }
    if len(context['city']):
        for city in context['city']:
            queries['cities'].append(Q(city__name=city))
    if len(context['province']):
        for province in context['province']:
            queries['provincies'].append(Q(city__province__name=province))
    if len(context['craft']):
        for craft in context['craft']:
            queries['crafts'].append(Q(name__icontsins=craft))
            # queries['crafts'].append(craft)
    if len(context['name']):
        for name in context['name']:
            queries['names'].append(Q(name__contains=name))
    return queries


def get_institutions(search):
    queries = get_q_queries(search)
    results = None
    if len(queries['cities']):
        results = Institution.objects.filter(reduce(or_, queries['cities']))
    if len(queries['provincies']):
        if results is None:
            results = Institution.objects.filter(reduce(or_, queries['provincies']))
            # TODO sprawdzanie zasięgu
    if len(queries['crafts']):
        if results is not None:
            # print(results.filter(institutioncraft__craft__name=queries['crafts']).query)
            results = results.filter(institutioncraft__craft__name__in=queries['crafts'])
    if len(queries['names']):
        if not results.filter(reduce(and_, queries['names'])).exists():
            results = Institution.objects.filter(reduce(and_, queries['names']))
        else:
            results = results.filter(reduce(and_, queries['names']))
    return results


def get_institutions2(search):
    context = get_search_context(search)
    results = None
    if len(context['city']):
        results = Institution.objects.filter(city__name__in=context['city'])
    if len(context['province']):
        if results is None:
            results = Institution.objects.filter(city__province__name__in=context['province'])

    if len(context['craft']):
        if results is not None:
            results = results.filter(institutioncraft__craft__name__in=context['craft'])
    if len(context['name']):
        if not results.filter(name__contains__in=context['name']).exists():
            results = Institution.objects.filter(name__contains__in=context['name'])
        else:
            results = results.filter(name__contains__in=context['name'])
    return results








