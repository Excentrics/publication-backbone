# -*- coding: utf-8 -*-
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import PromoPluginModel
from forms import PromoForm
from django.utils.translation import ugettext as _


@plugin_pool.register
class PromoPlugin(ContentPlugin):
    model = PromoPluginModel # Model where data about this plugin is saved
    category = _('Advanced')
    render_template = "publication_backbone/plugins/promo/promo.html"
    cache_output = False
    form=PromoForm


    def get_render_template(self, request, instance, **kwargs):

        if instance.get_template_name:
            return instance.get_template_name
        return self.render_template

    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """

        context = super(PromoPlugin, self).get_context(request, instance, **kwargs)

        COLUMN_DIVIDERS = [6,5,4,3,2]
        ic = instance.count
        divider = None
        for cd in COLUMN_DIVIDERS:
            n = ic % cd
            if n == 0:
                if cd != 6:
                    divider = cd
                    break
                else:
                    if ic > 12:
                        divider = cd
                        break

        #instance.category = instance.categories[0]
        categories = instance.categories.all()

        context.update({
            'instance': instance,
            'plugin_id': "%s" % instance.pk,
            'category': categories[0] if categories else None,
            'categories': categories,
            'divider': divider,
            'to_publication': instance.to_publication if instance.to_publication else None,
            })

        return context
