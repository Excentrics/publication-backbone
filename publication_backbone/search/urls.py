#-*- coding: utf-8 -*-

from django.conf.urls import patterns, include
from publication_backbone.backends_pool import backends_pool

urlpatterns = patterns('')

# For every backend defined in the backend pool, load all the URLs it defines
# in its get_urls() method.
for backend in backends_pool.get_search_backends_list():
    regexp = '^%s/' % backend.url_namespace
    urls = backend.get_urls()
    pattern = patterns('',
        (regexp, include(backend.get_urls()))
    )

    urlpatterns = pattern + urlpatterns
