# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_YANDEX_MAP_PLUGIN_TEMPLATE_CHOICES = (
        ('publication_backbone/plugins/yandex_map/default.html', _("Default yandex map template")),
        #('publication_backbone/plugins/yandex_map/simple.html', _("Simple yandex_map template")),
    )

YANDEX_MAP_TEMPLATE_CHOICES = getattr(settings, 'YANDEX_MAP_TEMPLATE_CHOICES',
    DEFAULT_YANDEX_MAP_PLUGIN_TEMPLATE_CHOICES)

YANDEX_MAP_TYPE_CHOICES = getattr(settings, 'YANDEX_MAP_TYPE_CHOICES',
    (('yandex#publicMap', _("public map")),
     ('yandex#map', _("schema map")),
     ('yandex#satellite', _("satellite map")),
     ('yandex#hybrid', _("hybrid map")),)
    )

YANDEX_MAP_MARKER_COLOR_CHOICES = getattr(settings, 'YANDEX_MAP_MARKER_COLOR_CHOICES',
    (('#FF0000', _("red")),
     ('#00FF00', _("green")),
     ('#0000FF', _("blue")),
     ('#FFED00', _("yellow")),)
    )