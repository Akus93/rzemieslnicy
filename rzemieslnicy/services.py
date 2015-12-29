from operator import and_
from django.db.models import Q
from functools import reduce

from .models import Institution, City, Province, Craft, InstitutionCraft


def pl_to_en(word):
    return word.translate(str.maketrans("ąćęłńóśżźĄĆĘŁŃÓŚŻŹ", "acelnoszzACELNOSZZ"))

# TODO WYSZUKIWANIE PO WOJEWODZTWIE odmiana wojewodztwa


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
        elif Province.objects.filter(name=word.capitalize()).exists():
            context['province'].append(word.capitalize())
        elif Craft.objects.filter(name=word.capitalize()).exists():
            context['craft'].append(word.capitalize())
        elif Institution.objects.filter(name__icontains=word).exists():
            context['name'].append(word)
    return context


def get_institutions(search):
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
        else:
            results = Institution.objects.filter(institutioncraft__craft__name__in=context['craft'])
    if len(context['name']):
        query = reduce(and_, (Q(name__icontains=x) for x in context['name']))
        if results is None:
            results = Institution.objects.filter(query)
        else:
            results = results.filter(query)
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





