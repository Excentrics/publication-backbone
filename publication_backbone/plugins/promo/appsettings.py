# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_PROMO_PLUGIN_TEMPLATE_CHOICES = (
        ('publication_backbone/plugins/promo/promo_default.html', _("Default promo")),
        ('publication_backbone/plugins/promo/promo_list.html', _("List promo")),
        ('publication_backbone/plugins/promo/promo.html', _("Top links promo")),
        ('publication_backbone/plugins/promo/promo_bottom.html', _("Bottom links promo")),
    )

PROMO_PLUGIN_TEMPLATE_CHOICES = getattr(settings, 'PROMO_PLUGIN_TEMPLATE_CHOICES', DEFAULT_PROMO_PLUGIN_TEMPLATE_CHOICES)