from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import SubMenu
import os


@plugin_pool.register
class SubMenuPlugin(ContentPlugin):
    """
    Plugin for rendering pictures.
    """
    model = SubMenu
    category = _('Main')
    render_template = "publication_backbone/plugins/sub_menu/default.html"

    def get_render_template(self, request, instance, **kwargs):

        if instance.get_template_name:
            return instance.get_template_name
        return self.render_template


    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """

        context = super(SubMenuPlugin, self).get_context(request, instance, **kwargs)
        context.update({
            'max_depth': instance.max_depth,
            'template': instance.template
        })

        return context