# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from publication_backbone.views import PublicationTemplateView


urlpatterns = patterns('',
    url(r'^terms-of-service/$',
        PublicationTemplateView.as_view(template_name="publication_backbone/terms_of_service.html"),
        name='terms_of_service'),
    url(r'^rubricator/', include('publication_backbone.urls.rubricator')),
    url(r'^category/', include('publication_backbone.urls.category')),
    url(r'^publications/', include('publication_backbone.urls.publication')),
    url(r'^promotion/', include('publication_backbone.urls.promotion')),
    url(r'^publication_group/', include('publication_backbone.urls.publication_group')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^forms/', include('form_designer.urls')),
    # Search
    url(r'^search/', include('publication_backbone.search.urls')),
    url(r'^votes/', include('publication_backbone.interview.urls')),

)

