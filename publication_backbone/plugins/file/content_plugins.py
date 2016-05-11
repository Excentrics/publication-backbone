from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import FileItem
import os
from django.db.models import Max


@plugin_pool.register
class FilePlugin(ContentPlugin):
    """
    Plugin for rendering pictures.
    """
    model = FileItem
    category = _('Main')
    render_template = "publication_backbone/plugins/file/default.html"

    def get_render_template(self, request, instance, **kwargs):

        if instance.get_template_name:
            return instance.get_template_name
        return self.render_template


    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """

        context = super(FilePlugin, self).get_context(request, instance, **kwargs)

        type_id = instance.polymorphic_ctype_id
        tpl = instance.template
        pos = instance.sort_order
        if pos == 0:
            before = False
        else:
            before = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, fileitem__template=tpl, sort_order__exact=pos-1).exists()
        after = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, fileitem__template=tpl, sort_order__exact=pos+1).exists()
        in_group = before or after

        files_group_key = 0

        if in_group:
            previous_non_file_object = instance.placeholder.contentitems.exclude(polymorphic_ctype_id=type_id).filter(sort_order__lt=pos).aggregate(sort_order=Max('sort_order'))
            if previous_non_file_object['sort_order'] is not None:
                files_group_key = previous_non_file_object['sort_order'] + 1

        context.update({
            'file': instance.file,
            'ext': os.path.splitext(instance.file.name)[1][1:],
            'in_group': in_group,
            'image_group_key': files_group_key,
            'is_first': not before,
            'is_last': not after
        })

        return context