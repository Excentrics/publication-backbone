# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import InterviewView

urlpatterns = patterns('',

    url(r'^(?P<pk>\d+)$',
        InterviewView.as_view(),
        name='interview_detail',
        ),
    url(r'^',
        InterviewView.as_view(),
        name='interview_vote',
        ),
    )
