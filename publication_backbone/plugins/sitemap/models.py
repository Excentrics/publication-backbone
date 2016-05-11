# -*- coding: utf-8 -*-
from django.db import models
from future.utils import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem
from . import appsettings


@python_2_unicode_compatible
class SitemapItem(ContentItem):
    """
    Sitemap
    """
    template = models.CharField(_("Template"), max_length=255, choices=appsettings.SITEMAP_PLUGIN_TEMPLATE_CHOICES, default=appsettings.SITEMAP_PLUGIN_TEMPLATE_CHOICES[0])

    class Meta:
        verbose_name = _("Sitemap")
        verbose_name_plural = _("Sitemaps")

    @property
    def get_template_name(self):
        return self.template

    def __str__(self):
        return str(self.pk)
