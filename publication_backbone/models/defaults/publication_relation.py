# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from publication_backbone.models_bases.publication import BasePublicationRelation


#==============================================================================
# BasePublicationRelation
#==============================================================================
class PublicationRelation(BasePublicationRelation):

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('publication relation')
        verbose_name_plural = _('publication relations')
        unique_together = ('from_publication', 'to_publication', 'rubric',)