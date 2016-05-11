# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from publication_backbone.models_bases.publication import BasePublicationImage


#==============================================================================
# PublicationImages
#==============================================================================
class PublicationImage(BasePublicationImage):

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('publication image')
        verbose_name_plural = _('publication images')
        ordering = ('sort',)

