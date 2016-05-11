# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from publication_backbone.views.publication_group import PublicationGroupHybridDetailView, PublicationGroupHybridListView

#

urlpatterns = patterns('',

    url(r'^$',
        PublicationGroupHybridListView.as_view(),
        name='publication_group_list'
        ),

    url(r'^-/(?P<pk>[0-9A-Za-z_.-]+)/$',
        PublicationGroupHybridDetailView.as_view(),#model=PublicationGroup
        name='publication_group_detail_by_pk'
        ),

    url(r'^(?P<slug>[0-9A-Za-z_.-]+)/$',
        PublicationGroupHybridDetailView.as_view(),#model=PublicationGroup
        name='publication_group_detail'
        ),

    )
