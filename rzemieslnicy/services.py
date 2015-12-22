from .models import Institution, City, Province, Craft


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
        elif Province.objects.filter(name=word.capitalize()).exists():
            context['province'].append(word.capitalize())
        elif Craft.objects.filter(name=word.capitalize()).exists():
            context['craft'].append(word.capitalize())
        elif Institution.objects.filter(name__contains=word).exists():
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
        if not results.filter(name__contains__in=context['name']).exists():
            results = Institution.objects.filter(name__contains__in=context['name'])
        else:
            results = results.filter(name__contains__in=context['name'])
    return results








