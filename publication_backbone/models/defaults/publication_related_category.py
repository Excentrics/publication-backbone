# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models

from publication_backbone.models_bases.publication import BasePublicationRelatedCategory
from publication_backbone.models import Publication


PUBLICATION_RELATED_CATEGORY_ORDER_CHOICES = tuple([(x['id'], x['name']) for x in Publication.objects.get_ordering_modes()])

#==============================================================================
# BasePublicationRelatedCategory
#==============================================================================
class PublicationRelatedCategory(BasePublicationRelatedCategory):
    order = models.CharField(verbose_name=_('Display Order'), max_length=255, blank=True,
                                choices=PUBLICATION_RELATED_CATEGORY_ORDER_CHOICES, default=PUBLICATION_RELATED_CATEGORY_ORDER_CHOICES[0][0])

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('publication related category')
        verbose_name_plural = _('publication related categories')
        unique_together = (("publication", "category"),)
