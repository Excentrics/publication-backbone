# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from publication_backbone.views.promotion import PromotionListHybridView


urlpatterns = patterns('',
    url(r'^js/(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?(?:set/(?P<set>[;\d]+)/)?(?:group/(?P<group_id>[0-9A-Za-z-_.]+)/)?(?:subj/(?P<subj>[;\d]+)/)?(?:rel/(?P<rel>[;bfr\d]+)/)?$',
        PromotionListHybridView.as_view(initial_data={
            'format': 'js'
        }),
        name='publication_promotion_list_js'
        ),
    url(r'^(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?(?:set/(?P<set>[;\d]+)/)?(?:group/(?P<group_id>[0-9A-Za-z-_.]+)/)?(?:subj/(?P<subj>[;\d]+)/)?(?:rel/(?P<rel>[;bfr\d]+)/)?$',
        PromotionListHybridView.as_view(),
        name='publication_promotion_list'
        ),
    )
