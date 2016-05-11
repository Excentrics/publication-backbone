#-*- coding: utf-8 -*-
import os
from django.core.files.images import ImageFile
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles import finders
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from polymorphic.base import PolymorphicModelBase


def get_base_polymorphic_model(ChildModel):
    """
    First model in the inheritance chain that inherited from the PolymorphicMPTTModel
    """
    for Model in reversed(ChildModel.mro()):
        if isinstance(Model, PolymorphicModelBase) and not Model._meta.abstract:
            return Model
    return None


#==============================================================================
# PolymorphicModelMixin
#==============================================================================
class PolymorphicModelMixin(object):
    """
    The mixin class for polymorphic.PolymorphicModel
    """

    def get_real_instance_class(self):
        if not hasattr(self, '_real_instance_class_cache'):
            if self.polymorphic_ctype_id is not None:
                self._real_instance_class_cache = super(PolymorphicModelMixin, self).get_real_instance_class()
            else:
                self._real_instance_class_cache = self.__class__
        return self._real_instance_class_cache

    def get_real_instance(self):
        if not hasattr(self, '_real_instance_cache'):
            self._real_instance_cache = super(PolymorphicModelMixin, self).get_real_instance()
        return self._real_instance_cache

    def get_base_instance_class(self):
        if not hasattr(self, '_base_instance_class_cache'):
            self._base_instance_class_cache = get_base_polymorphic_model(self.__class__)
        return self._base_instance_class_cache

    def get_base_instance(self):
        if not hasattr(self, '_base_instance_cache'):
            model_class = self.get_base_instance_class()
            try:
                self._base_instance_cache = model_class.objects.non_polymorphic().get(pk=self.pk)
            except model_class.DoesNotExist:
                self._base_instance_cache = self.get_base_instance_class()()
        return self._base_instance_cache

    def get_real_instance_class_name(self):
        return self.get_real_instance_class().__name__

    def get_real_instance_class_name_display(self):
        return self.get_real_instance_class()._meta.verbose_name
    get_real_instance_class_name_display.short_description = _('type')


#==============================================================================
# PlaceholderImageMixin
#==============================================================================
class PlaceholderImageMixin(object):
    """
    The mixin class for polymorphic.BasePublication
    """
    PLACEHOLDER_IMAGE_PATH = getattr(settings, 'PLACEHOLDER_IMAGE_PATH', 'publication_backbone/images/noimage.png')

    def get_placeholder_image(self):
        if not hasattr(self.__class__, '_PlaceholderImageMixin__placeholder_image_cache'):
            path = finders.find(self.PLACEHOLDER_IMAGE_PATH)
            if path:
                location, file_name = os.path.split(path)
                fs = FileSystemStorage(location=location)
                image = ImageFile(fs.open(file_name))
                image.storage = fs
                self.__class__.__placeholder_image_cache = image
            else:
                self.__class__.__placeholder_image_cache = None

        return self.__class__.__placeholder_image_cache