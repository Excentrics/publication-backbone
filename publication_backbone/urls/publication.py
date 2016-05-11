# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from publication_backbone.views.publication import (PublicationListHybridView,
                                                    PublicationHybridDetailView,
                                                    PublicationListCommonJsView,
                                                    PublicationRssFeed)


urlpatterns = patterns('',
    url(r'^js/common/$',
        PublicationListCommonJsView.as_view(),
        name='catalog_common_js'
        ),
    url(r'^js/(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?(?:set/(?P<set>[;\d]+)/)?(?:group/(?P<group_id>[0-9A-Za-z_.-]+)/)?(?:subj/(?P<subj>[;\d]+)/)?(?:rel/(?P<rel>[;bfr\d]+)/)?$',
        PublicationListHybridView.as_view(initial_data={
            'format': 'js'
        }),
        name='publication_list_js'
        ),
    url(r'^(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?(?:set/(?P<set>[;\d]+)/)?(?:group/(?P<group_id>[0-9A-Za-z_.-]+)/)?(?:subj/(?P<subj>[;\d]+)/)?(?:rel/(?P<rel>[;bfr\d]+)/)?$',
        PublicationListHybridView.as_view(),
        name='publication_list'
        ),
    url(r'^(?:(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?-/(?P<pk>[0-9]+)/$',
        PublicationHybridDetailView.as_view(),#model=Publication
        name='publication_detail_by_pk'
        ),
    url(r'^(?:(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?publication/(?P<slug>[0-9A-Za-z_.-]+)/$',
        PublicationHybridDetailView.as_view(),#model=Publication
        name='publication_detail'
        ),
    url(r'^feed/$',
        PublicationRssFeed(),
        name='rss_feed'),
    )
