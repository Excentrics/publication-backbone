# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import ImageField
from publication_backbone.models_bases.publication_group import BasePublicationGroup
from publication_backbone.models_bases.managers import PublicationGroupManager
from publication_backbone.utils.media import get_media_path


#==============================================================================
# Publication
#==============================================================================
class PublicationGroup(BasePublicationGroup):

    image = ImageField(verbose_name=_('image'), upload_to=get_media_path, blank=True)

    objects = PublicationGroupManager()

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('publication group')
        verbose_name_plural = _('publication groups')

    def get_image(self):
        if not hasattr(self, '_PublicationGroup__image_cache'):
            if self.image:
                self.__image_cache = self.image
            else:
                try:
                    img = self.publications.exclude(image__exact='').exclude(image__isnull=True).values_list('image', flat=True).order_by('-date_added')[0]
                except IndexError:
                    img = None
                self.__image_cache = img if img else super(PublicationGroup, self).get_image()
        return self.__image_cache
