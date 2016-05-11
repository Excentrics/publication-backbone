from django.db import models
from future.utils import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem
from publication_backbone.utils.media import get_media_path


@python_2_unicode_compatible
class ContentGapItem(ContentItem):
    """
    Content gap item
    """

    css_class = models.CharField(_("CSS class"), help_text=_('CSS class for container'), blank=True, max_length=255)
    attributes = models.CharField(_("Attributes"), help_text=_('Attributes for container'), blank=True, max_length=255)
    image = models.ImageField(_("Background image"), help_text=_('Image for container background'), blank=True, upload_to=get_media_path)

    class Meta:
        verbose_name = _("Content gap")
        verbose_name_plural = _("Content gaps")

    def __str__(self):
        return str("Content gap")