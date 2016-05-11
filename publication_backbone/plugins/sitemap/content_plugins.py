# -*- coding: utf-8 -*-
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import SitemapItem


@plugin_pool.register
class SitemapPlugin(ContentPlugin):
    """
    Plugin for rendering pictures.
    """
    model = SitemapItem
    category = _('Advanced')
    cache_output = not settings.DEBUG
    render_template = "publication_backbone/plugins/sitemap/default.html"


    def get_render_template(self, request, instance, **kwargs):

        if instance.get_template_name:
            return instance.get_template_name
        return self.render_template

