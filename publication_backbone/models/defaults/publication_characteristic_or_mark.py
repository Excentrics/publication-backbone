# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from publication_backbone.models_bases.publication import BaseAdditionalPublicationCharacteristicOrMark


#==============================================================================
# PublicationCharacteristicOrMark
#==============================================================================
class PublicationCharacteristicOrMark(BaseAdditionalPublicationCharacteristicOrMark):

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('additional publication charsc or mark')
        verbose_name_plural = _('additional publication chars or marks')
        unique_together = ('publication', 'rubric',)