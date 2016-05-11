from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem
from future.utils import python_2_unicode_compatible
from future.builtins import str
from . import appsettings


@python_2_unicode_compatible
class YandexMapItem(ContentItem):
    """
    Yandex map
    """

    caption = models.CharField(_("caption"), blank=True, max_length=255)
    address = models.CharField(_("address"), blank=True, max_length=255)
    latitude = models.CharField(_("latitude"), blank=True, max_length=25)
    longitude = models.CharField(_("longitude"), blank=True, max_length=25)
    zoom = models.PositiveIntegerField(_("zoom"), default=15)
    map_type = models.CharField(_("map_type"), max_length=50, choices=appsettings.YANDEX_MAP_TYPE_CHOICES, default=appsettings.YANDEX_MAP_TYPE_CHOICES[0][0])
    color = models.CharField(_("marker color"), max_length=10, choices=appsettings.YANDEX_MAP_MARKER_COLOR_CHOICES, default=appsettings.YANDEX_MAP_MARKER_COLOR_CHOICES[0][0])
    template = models.CharField(_("Template"), max_length=255, choices=appsettings.YANDEX_MAP_TEMPLATE_CHOICES, default=appsettings.YANDEX_MAP_TEMPLATE_CHOICES[0][0])


    class Meta:
        verbose_name = _("Yandex Map")
        verbose_name_plural = _("Yandex Maps")


    def __str__(self):
        return self.caption or str("Yandex Map")

    @property
    def get_template_name(self):
        return self.template
