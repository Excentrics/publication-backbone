# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

#from publication_backbone.models import Rubric

from publication_backbone.views.rubricator import (
    RubricHybridDetailView,
    RubricHybridListView,
    RubricatorCommonJsView)


urlpatterns = patterns('',
    url(r'^js/common/$', RubricatorCommonJsView.as_view(), name='rubricator_common_js'), # Common js requirements
    url(r'^js/(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?(?:set/(?P<set>[;\d]+)/)?$',
        RubricHybridListView.as_view(initial_data={
            'format': 'js'
        }),
        name='rubric_list_js'
        ),
    url(r'^(?:path/(?P<path>.+?)/)?(?:selected/(?P<selected>\d+)/)?(?:set/(?P<set>[;\d]+)/)?$',
        RubricHybridListView.as_view(),#model=Rubric
        name='rubric_list'
        ),
    url(r'^(?P<pk>\d+)/$',
        RubricHybridDetailView.as_view(),#model=Rubric
        name='rubric_detail'
        ),
    )