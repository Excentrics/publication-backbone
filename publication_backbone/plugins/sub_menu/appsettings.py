# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_SUBMENU_PLUGIN_TEMPLATE_CHOICES = (
        ('publication_backbone/plugins/sub_menu/default.html', _("Default sub menu")),
        ('publication_backbone/plugins/sub_menu/horizontal.html', _("As string submenu")),
    )

SUBMENU_PLUGIN_TEMPLATE_CHOICES = getattr(settings, 'SUBMENU_PLUGIN_TEMPLATE_CHOICES', DEFAULT_SUBMENU_PLUGIN_TEMPLATE_CHOICES)