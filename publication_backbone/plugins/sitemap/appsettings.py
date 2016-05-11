# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_SITEMAP_PLUGIN_TEMPLATE_CHOICES = (
        ('publication_backbone/plugins/sitemap/default.html', _("Default sitemap")),
    )

SITEMAP_PLUGIN_TEMPLATE_CHOICES = getattr(settings, 'PICTURE_PLUGIN_TEMPLATE_CHOICES', DEFAULT_SITEMAP_PLUGIN_TEMPLATE_CHOICES)