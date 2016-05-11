# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
"""
``rebuild_rubricator``
---------------------

``rebuild_rubricator`` rebuilds your mptt pointers. Only use in emergencies.
"""

from django.core.management.base import NoArgsCommand

from publication_backbone.models import Rubric

class Command(NoArgsCommand):
    help = "Run this manually to rebuild your mptt pointers. Only use in emergencies."

    def handle_noargs(self, **options):
        print "Rebuilding MPTT pointers for Rubric"
        Rubric._tree_manager.rebuild()
