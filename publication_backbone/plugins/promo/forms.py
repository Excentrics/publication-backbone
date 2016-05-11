# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib import admin
from publication_backbone.models import Publication
from .models import PromoPluginModel
from salmonella.widgets import SalmonellaIdWidget
from fluent_contents.forms import ContentItemForm


#==============================================================================
# PromoForm
#==============================================================================
class PromoForm(ContentItemForm):
    to_publication = forms.ModelChoiceField(queryset=Publication.objects.all(), required=False,
                                        widget=SalmonellaIdWidget(PromoPluginModel._meta.get_field("to_publication").rel, admin.site),
                                        label=_('Related publication'))
