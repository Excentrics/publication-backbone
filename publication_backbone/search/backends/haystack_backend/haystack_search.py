# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from publication_backbone import conf as config
from .views import PublicationSearchView, autocomplete
from .forms import PublicationSearchForm


class HaystackSearchBackend(object):

    backend_name = "Haystack Search"
    backend_verbose_name = _("Haystack Search")
    url_namespace = "haystacksearch"

    def __init__(self, publication_backbone):
        self.publication_backbone = publication_backbone
        # This is the publication_backbone reference, it allows this backend to interact with
        # it in a tidy way (look ma', no imports!)

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', PublicationSearchView(form_class = PublicationSearchForm), name='haystacksearch'),
            url(r'^autocomplete/$', autocomplete),
        )
        return urlpatterns