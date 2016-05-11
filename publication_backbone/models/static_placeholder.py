# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from publication_backbone.utils.contrib import get_unique_slug
from django.db import models
from django.contrib.sites.models import Site
from fluent_contents.models import PlaceholderField
from django.core import validators


#==============================================================================
# Publication
#==============================================================================
class StaticPlaceholder(models.Model):
    name = models.CharField(_("Placeholder title"), max_length=200, blank=False)
    slug = models.CharField(_("Placeholder name"), max_length=100, blank=False, help_text=_("Only in latin charset a-z"), validators=[validators.validate_slug])
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name=_('site'))
    placeholder = PlaceholderField("placeholder_content", verbose_name=_('content'))

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('placeholder')
        verbose_name_plural = _('placeholders')
        unique_together = ("name", "site")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Overridden model save function"""
        if not self.slug:
            self.slug = get_unique_slug(self.name)
        return super(StaticPlaceholder, self).save(*args, **kwargs)
