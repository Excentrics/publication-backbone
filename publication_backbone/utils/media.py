import os
import datetime
from pytils.translit import slugify
from django.conf import settings
from publication_backbone.utils.contrib import create_uid

#==============================================================================
# get_media_path
#==============================================================================
def get_media_path(instance, filename):
    i = filename.rfind('.')
    filename = '%s%s' % (slugify(filename[:i]), filename[i:])
    today = datetime.datetime.now()
    DIRECTORY_MEDIA_PATH = getattr(settings, "PUBLICATION_BACKBONE_MEDIA_PATH", "publication_backbone_media/")
    media_path = os.path.join(DIRECTORY_MEDIA_PATH, str(today.year), str(today.month), str(today.day))
    len_media_path = len(media_path)
    len_filename = len(filename)
    if (len_media_path + len_filename) > 100:
        i = filename.rfind('.')
        delta = 67 - len_media_path - (len_filename - i)
        # 100(max imagefield size) - 32(hex hash for unique filename) - len_media_path - (len_filename - i)(characters for file extensions)
        filename = filename[:delta] + create_uid() + filename[i:]
    full_path = os.path.join(media_path, filename)
    return full_path