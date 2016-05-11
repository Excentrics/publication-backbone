# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models

from sorl.thumbnail import ImageField

from publication_backbone.models_bases.rubricator import (
    BaseRubric,
    DeterminantFilteringMixin,
    )
from publication_backbone.models_bases.managers import RubricManager
from publication_backbone.utils.media import get_media_path


class Rubric(DeterminantFilteringMixin, BaseRubric):

    image = ImageField(verbose_name=_('image'), upload_to=get_media_path, blank=True)

    objects = RubricManager()

    # Fix a problem in the deletion collector of the Django ORM. Workaround for https://github.com/chrisglass/django_polymorphic/issues/34
    _base_manager = models.Manager()

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('rubric')
        verbose_name_plural = _('publication rubricator')

    def get_image(self):
        if not hasattr(self, '_Rubric__image_cache'):
            self.__image_cache = self.image
        return self.__image_cache

