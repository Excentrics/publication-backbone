from django.db import models
from future.utils import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem
from . import appsettings
from future.builtins import str

@python_2_unicode_compatible
class SubMenu(ContentItem):
    """
    Sub menu plugin model
    """
    max_depth = models.PositiveIntegerField(_("Max depth"), default=1)
    template = models.CharField(_("Template"), max_length=255, choices=appsettings.SUBMENU_PLUGIN_TEMPLATE_CHOICES,
                                default=appsettings.SUBMENU_PLUGIN_TEMPLATE_CHOICES[0])


    class Meta:
        verbose_name = _("Sub menu")
        verbose_name_plural = _("Sub menus")

    def __str__(self):
        return str(self._meta.verbose_name)

    @property
    def get_template_name(self):
        return self.template