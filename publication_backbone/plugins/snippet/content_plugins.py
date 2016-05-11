"""
Definition of the plugin.
"""
from django.utils.safestring import mark_safe
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.forms import ContentItemForm
from .models import SnippetItem
from django.utils.translation import ugettext_lazy as _
from django_ace import AceWidget
from django import forms


class SnippetForm(ContentItemForm):
    html = forms.CharField(
        widget=AceWidget(theme='eclipse', mode='html', wordwrap=True, width="100%", height="300px", showprintmargin=False),
        label=_("HTML code"),
        help_text=_("Enter the HTML code to display, like the embed code of an online widget."),
        required=False
    )


@plugin_pool.register
class SnippetPlugin(ContentPlugin):
    """
    Plugin for rendering raw HTML output.
    This can be used to insert embed codes in a webpage,
    for example for Google Docs, YouTube or SlideShare.
    """
    model = SnippetItem
    category = _('Advanced')
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS
    #form = SnippetForm

    def render(self, request, instance, **kwargs):
        return mark_safe(instance.html)

