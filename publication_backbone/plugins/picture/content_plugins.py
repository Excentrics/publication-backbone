from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import PictureItem
from django.db.models import Max


@plugin_pool.register
class PicturePlugin(ContentPlugin):
    """
    Plugin for rendering pictures.
    """
    model = PictureItem
    category = _('Main')
    render_template = "publication_backbone/plugins/picture/default.html"


    def get_render_template(self, request, instance, **kwargs):

        if instance.get_template_name:
            return instance.get_template_name
        return self.render_template


    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """
        type_id = instance.polymorphic_ctype_id
        tpl = instance.template
        pos = instance.sort_order
        if pos == 0:
            before = False
        else:
            before = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, pictureitem__template=tpl, sort_order__exact=pos-1).exists()
        after = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, pictureitem__template=tpl, sort_order__exact=pos+1).exists()
        in_group = before or after

        image_group_key = 0

        if in_group:
            previous_non_image_object = instance.placeholder.contentitems.exclude(polymorphic_ctype_id=type_id).filter(sort_order__lt=pos).aggregate(sort_order=Max('sort_order'))
            if previous_non_image_object['sort_order'] is not None:
                image_group_key = previous_non_image_object['sort_order'] + 1
        try:
            photo_reporting = request.photo_reporting if request.photo_reporting else False
        except:
            photo_reporting = False

        return {
            'instance': instance,
            'in_group': in_group,
            'image_group_key': image_group_key,
            'is_first': not before,
            'is_last': not after,
            'col_md': request.col_md if request.col_md else 12,
            'tag_name': request.tag_name if request.tag_name else 'div',
            'photo_reporting': photo_reporting,
        }