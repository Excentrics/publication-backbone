from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem



class VideoItem(ContentItem):
    """
    Display a Video
    """

    video_url = models.CharField(verbose_name=_('Youtube video code'), blank=False, max_length=255, help_text=_('For example: 0PJBSRAzQKs'))
    width = models.PositiveIntegerField(verbose_name=_('Video width'), default=560, blank=False)
    height = models.PositiveIntegerField(verbose_name=_('Video height'), default=315, blank=False)
    title = models.CharField(verbose_name=_("title"), blank=True, max_length=255)
    author = models.CharField(verbose_name=_('author'), blank=True, max_length=255)
    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")

    def __unicode__(self):
        if self.title:
            return self.title
        return "%s: %s" % (_("Video"), unicode(self.video_url))

