# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models_bases.category import LinkMixIn
from publication_backbone.models import BaseCategory



#==============================================================================
# CategoryLink
#==============================================================================
class CategoryLink(BaseCategory, LinkMixIn):

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('link')
        verbose_name_plural = _('links')

