# -*- coding: utf-8 -*-
import os
from binascii import hexlify
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models import BaseCategory


#==============================================================================
# Divider
#==============================================================================
class CategoryDivider(BaseCategory):

    can_have_children = False

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('divider')
        verbose_name_plural = _('categories dividers')

    def _create_slug(self):
        return hexlify(os.urandom(16))

    def _create_name(self):
        return _('_'*9)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not force_update and not force_insert:
            if not self.slug:
                self.slug = self._create_slug()
            if not self.name:
                self.name = self._create_name()
        return super(CategoryDivider, self).save(force_insert, force_update, *args, **kwargs)

