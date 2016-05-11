from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import VideoItem


@plugin_pool.register
class VideoPlugin(ContentPlugin):
    """
    Plugin for rendering VideoItem.
    """
    model = VideoItem
    category = _('Advanced')
    render_template = "publication_backbone/plugins/video/video.html"


    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """
        return {
            'instance': instance,
        }