from django.db import models
from future.utils import python_2_unicode_compatible
from future.builtins import str
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import PluginImageField, PluginUrlField
from fluent_contents.models.db import ContentItem
from django.conf import settings
from publication_backbone.utils.media import get_media_path
from . import appsettings


@python_2_unicode_compatible
class PictureItem(ContentItem):
    """
    Display a picture
    """

    image = models.ImageField(_("Image"), upload_to=get_media_path)
    caption = models.CharField(_("Caption"), blank=True, max_length=255)
    author = models.CharField(_("Author"), blank=True, max_length=255)
    template = models.CharField(_("Template"), max_length=255, choices=appsettings.PICTURE_PLUGIN_TEMPLATE_CHOICES, default=appsettings.PICTURE_PLUGIN_TEMPLATE_CHOICES[0])
    url = PluginUrlField(_("URL"), blank=True)

    class Meta:
        verbose_name = _("Picture")
        verbose_name_plural = _("Pictures")

    def __str__(self):
        return self.caption or str(self.image)

    @property
    def get_template_name(self):
        return self.template