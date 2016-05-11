from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import YandexMapItem


@plugin_pool.register
class YandexMapPlugin(ContentPlugin):
    """
    Plugin for rendering pictures.
    """
    model = YandexMapItem
    category = _('Advanced')
    render_template = "publication_backbone/plugins/yandex_map/default.html"


    class FrontendMedia:
        js = (
            '//api-maps.yandex.ru/2.1/?lang=ru_RU',
        )


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
        pos = instance.sort_order
        if pos == 0:
            before = False
        else:
            before = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, sort_order__exact=pos-1).exists()
        after = instance.placeholder.contentitems.filter(polymorphic_ctype_id=type_id, sort_order__exact=pos+1).exists()

        in_group = before or after


        context = super(YandexMapPlugin, self).get_context(request, instance, **kwargs)

        context.update({
            'in_group': in_group,
            'is_first': not before,
            'is_last': not after
        })


        return context