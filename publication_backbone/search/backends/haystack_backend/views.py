# -*- coding: utf-8 -*-
from haystack.views import SearchView
import simplejson as json
from django.http import HttpResponse
from haystack.query import SearchQuerySet
from publication_backbone import conf as config


def autocomplete(request):
    results_for_show = config.PUBLICATION_BACKBONE_LIVE_SEARCH_RESULTS
    sqs = SearchQuerySet().autocomplete(text=request.GET.get('q', ''))
    if results_for_show > 0:
        queryset_results = sqs[:int(results_for_show)]
    else:
        queryset_results = sqs
    suggestions = [{'title': result.title, 'url': result.object.get_absolute_url()} for result in queryset_results]
    the_data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(the_data, content_type='application/json')


class PublicationSearchView(SearchView):
    pass