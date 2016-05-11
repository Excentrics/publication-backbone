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
class FileItem(ContentItem):
    """
    File plugin model
    """

    file = models.FileField(_("File"), upload_to=get_media_path)
    caption = models.CharField(_("Caption"), blank=True, max_length=255)
    template = models.CharField(_("Template"), max_length=255, choices=appsettings.FILE_PLUGIN_TEMPLATE_CHOICES,
                                default=appsettings.FILE_PLUGIN_TEMPLATE_CHOICES[0])


    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")

    def __str__(self):
        return self.caption or str(self.file)

    @property
    def get_template_name(self):
        return self.template