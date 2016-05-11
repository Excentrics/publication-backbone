# -*- coding: utf-8 -*-
from django import VERSION as django_version
from django.views.generic import (TemplateView, ListView, DetailView, View)
from django.views.generic.base import TemplateResponseMixin


class PublicationTemplateView(TemplateView):
    """
    A class-based view for use within the Publication (this allows to keep the above
    import magic in only one place)

    As defined by
    http://docs.djangoproject.com/en/dev/topics/class-based-views/

    Stuff defined here (A.K.A this is a documentation proxy for the above
    link):
    ---------------------------------------------------------------------
    self.template_name : Name of the template to use for rendering
    self.get_context_data(): Returns the context {} to render the template with
    self.get(request, *args, **kwargs): called for GET methods
    """


class PublicationListView(ListView):
    """
    This is just to abstract the "Django version switching magic happening up
    there
    """


class PublicationDetailView(DetailView):
    """
    This is just to abstract the "Django version switching magic happening up
    there
    """


class PublicationView(View):
    """
    An abstraction of the basic view
    """


class PublicationTemplateResponseMixin(TemplateResponseMixin):
    """
    An abstraction to solve the import problem for the template response mixin
    """