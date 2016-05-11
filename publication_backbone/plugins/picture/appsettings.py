# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_PICTURE_PLUGIN_TEMPLATE_CHOICES = (
        ('publication_backbone/plugins/picture/default.html', _("Thumbnail picture / Gallery")),
        ('publication_backbone/plugins/picture/slider.html', _("Simple picture / Slider")),
        #('publication_backbone/plugins/picture/simple.html', _("Simple picture")),
    )

PICTURE_PLUGIN_TEMPLATE_CHOICES = getattr(settings, 'PICTURE_PLUGIN_TEMPLATE_CHOICES', DEFAULT_PICTURE_PLUGIN_TEMPLATE_CHOICES)