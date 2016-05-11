# -*- coding: utf-8 -*-
from django.contrib.sitemaps import GenericSitemap
from publication_backbone.models import Publication, Category
from fluent_pages.sitemaps import PageSitemap


class CategorySitemap(GenericSitemap):

    def location(self, obj):
        return obj.get_catalog_url()


class PublicationSitemap(GenericSitemap):

    limit = 1000


category_dict = {
    'queryset': Category.objects.all(),
    'date_field': 'creation_date',
    }

publication_dict = {
    'queryset': Publication.objects.active().order_by('-last_modified'),
    'date_field': 'last_modified',
    }

pages_dict = {
    'pages': PageSitemap,
}

sitemaps = {
    'pages': PageSitemap,
    'category': CategorySitemap(category_dict),
    'publications': PublicationSitemap(publication_dict),
    }
