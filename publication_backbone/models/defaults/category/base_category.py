# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models

from publication_backbone.models_bases.category import AbstractBaseCategory
from publication_backbone.models_bases.managers import BaseCategoryManager


#==============================================================================
# Base Category
#==============================================================================
class BaseCategory(AbstractBaseCategory):

    objects = BaseCategoryManager()

    # Fix a problem in the deletion collector of the Django ORM. Workaround for https://github.com/chrisglass/django_polymorphic/issues/34
    _base_manager = models.Manager()

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('base category')
        verbose_name_plural = _('base categories')
