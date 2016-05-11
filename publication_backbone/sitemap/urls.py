# -*- coding: utf-8 -*-
from django.conf.urls import *
from publication_backbone.sitemap import sitemaps


urlpatterns = patterns('django.contrib.sitemaps.views',
                      url(r'^sitemap\.xml$', 'index', {'sitemaps': sitemaps}),
                      url(r'^sitemap-(?P<section>.+)\.xml$', 'sitemap', {'sitemaps': sitemaps}))
