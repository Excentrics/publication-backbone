"""
Definition of the plugin.
"""
from fluent_contents.extensions import ContentPlugin, plugin_pool
from .models import TextItem
from django.utils.translation import ugettext_lazy as _


@plugin_pool.register
class TextPlugin(ContentPlugin):
    model = TextItem
    admin_init_template = "publication_backbone/plugins/text/admin_init.html"
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS
    category = _('Main')
    render_template = "publication_backbone/plugins/text/text.html"


    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """
        #try:
        #    news_type = instance.placeholder.parent.get_real_instance_class_name()
        #except:
        #    news_type = None

        return {
            'instance': instance,
        }