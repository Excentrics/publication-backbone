# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem
from mptt.fields import TreeManyToManyField
from future.utils import python_2_unicode_compatible
from future.builtins import str
from publication_backbone.utils.loader import get_publication_backbone_model_string
from publication_backbone.models import Publication
from . import appsettings

EX_PROMO_ORDER_CHOICES = tuple([(x['id'], x['name']) for x in Publication.objects.get_ordering_modes()])


@python_2_unicode_compatible
class PromoPluginModel(ContentItem):

    categories = TreeManyToManyField(get_publication_backbone_model_string('Category'), verbose_name=_('categories'),
                                     related_name='fluent_promotions', null=True, blank=True)
    count = models.PositiveIntegerField(_("Display count"), default=5)
    order = models.CharField(verbose_name=_('Display Order'), max_length=255, blank=True,
                                choices=EX_PROMO_ORDER_CHOICES, default=EX_PROMO_ORDER_CHOICES[0][0])
    to_publication = models.ForeignKey(get_publication_backbone_model_string('Publication'),
                                related_name='promo_publication_relation', verbose_name=_('to publication'), null=True, blank=True)
    template = models.CharField(_("Template"), max_length=255, choices=appsettings.PROMO_PLUGIN_TEMPLATE_CHOICES,
                                default=appsettings.PROMO_PLUGIN_TEMPLATE_CHOICES[0])


    class Meta:
        verbose_name = _('Promo Plugin')
        verbose_name_plural = _('Promo Plugins')

    def __str__(self):
        return str(self.pk)

    @property
    def get_template_name(self):
        return self.template