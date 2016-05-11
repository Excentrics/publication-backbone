# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from sorl.thumbnail import ImageField

from publication_backbone.models_bases.publication import (
    BasePublication,
)
from publication_backbone.models_bases.managers import PublicationManager
from publication_backbone.utils.media import get_media_path
from publication_backbone.utils.contrib import get_unique_slug
from django.db.models import Q
from operator import or_

#==============================================================================
# Publication
#==============================================================================
class Publication(BasePublication):

    image = ImageField(verbose_name=_('image'), upload_to=get_media_path, blank=True, help_text=_("This image used in publication list as main image of publication"))

    objects = PublicationManager()

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('publication')
        verbose_name_plural = _('Publications')

    def get_image(self):
        if not hasattr(self, '_Publication__image_cache'):
            if self.image:
                self.__image_cache = self.image
            else:
                images = super(Publication, self).get_images()
                self.__image_cache = images[0].picture if images else None
        return self.__image_cache

    def get_images(self):
        if not hasattr(self, '_Publication__images_cache'):
            self.__images_cache = super(Publication, self).get_images()
            if not self.__images_cache:
                image = self.get_image()
                if image:
                    self.__images_cache = [{'picture': image, 'caption': self.get_name()},]
        return self.__images_cache

    def get_related_by_tags_publications(self):
        """
        Return all publications related by tags with current publication
        """
        if not hasattr(self, '_Publication__related_publications_cache'):
            if self.tags and self.tags.strip():
                tags_list = [x for x in [x.strip() for x in self.tags.split(';')] if x != u'']
                self.__related_publications_cache = Publication.objects.active().exclude(pk=self.pk).\
                    filter(reduce(or_, [Q(tags__icontains=c) for c in tags_list])).\
                    make_ordering('date_added_desc')[:5]
            else:
                self.__related_publications_cache = None

        return self.__related_publications_cache

    def save(self, *args, **kwargs):
        """Overridden model save function"""
        if not self.slug:
            self.slug = get_unique_slug(self.name)
        return super(Publication, self).save(*args, **kwargs)
