from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import ContentGapItem


@plugin_pool.register
class ContentGapPlugin(ContentPlugin):
    """
    Plugin for rendering content gap.
    """
    model = ContentGapItem
    category = _('Advanced')
    render_template = "publication_backbone/plugins/contentgap/default.html"

    def get_render_template(self, request, instance, **kwargs):
        return self.render_template


    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """
        type_id = instance.polymorphic_ctype_id
        pos = instance.sort_order
        after = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, sort_order__gt=pos).exists()
        before = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, sort_order__lt=pos).exists()

        return {
            'instance': instance,
            'is_last': not after,
            'is_first': not before,
            'col_md': request.col_md if hasattr(request, "col_md") else 12,
            'tag_name': request.tag_name if hasattr(request, "tag_name") else 'div',
            'is_publication': request.is_publication if hasattr(request, "is_publication") else False
        }