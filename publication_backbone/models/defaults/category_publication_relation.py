# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models_bases.publication import BaseCategoryPublicationRelation


#==============================================================================
# CategoryPublicationRelation
#==============================================================================
class CategoryPublicationRelation(BaseCategoryPublicationRelation):

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('category publication relation')
        verbose_name_plural = _('category publication relations')

