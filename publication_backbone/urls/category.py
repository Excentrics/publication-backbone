# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

#from publication_backbone.models import BaseCategory

from publication_backbone.views.category import (
    CategoryHybridDetailView,
    CategoryHybridListView,
    CategoryCommonJsView,
    )


urlpatterns = patterns('',
    url(r'^js/common/$',
        CategoryCommonJsView.as_view(),
        name='category_common_js'
        ),
    url(r'^js/(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?$',
        CategoryHybridListView.as_view(initial_data={
            'format': 'js'
        }),
        name='category_list_js'
        ),
    url(r'^(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?$',
        CategoryHybridListView.as_view(),
        name='category_list'
        ),
    url(r'^(?P<pk>\d+)/$',
        CategoryHybridDetailView.as_view(),#model=BaseCategory
        name='category_detail',
        ),
    )
