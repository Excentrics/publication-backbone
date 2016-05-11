# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_FILE_PLUGIN_TEMPLATE_CHOICES = (
        ('publication_backbone/plugins/file/default.html', _("Default file")),
        ('publication_backbone/plugins/file/hidden.html', _("Hidden file")),
    )

FILE_PLUGIN_TEMPLATE_CHOICES = getattr(settings, 'FILE_PLUGIN_TEMPLATE_CHOICES', DEFAULT_FILE_PLUGIN_TEMPLATE_CHOICES)