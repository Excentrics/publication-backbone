#-*- coding: utf-8 -*-
"""
``make_rubrics_by_publications_attributes``
---------------------

``make_rubrics_by_publications_attributes`` - make sub rubrics structure by additional publications attributes.
"""

from django.core.management.base import NoArgsCommand, CommandError

from optparse import make_option

from pytils.translit import slugify

from publication_backbone.models import Rubric, PublicationCharacteristicOrMark
from publication_backbone.models import Facet

from django.utils.translation import ugettext


class Command(NoArgsCommand):
    help = ugettext("Make sub rubrics structure by additional publications attributes.")

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--target',
            dest='target_id',
            type=long,
            default=None,
            help=ugettext('Target rubric id')
        ),
    )

    def get_rubric_by_id(self, id):
        try:
            return Rubric.objects.get(pk=id)
        except Rubric.DoesNotExist:
            raise CommandError(ugettext('No %(model)s matches the given `id`=`%(id)s`.') % {
                'model': Rubric._meta.object_name,
                'id': id})

    def handle_noargs(self, **options):
        target_id = options.get('target_id')
        if target_id is None:
            raise CommandError(ugettext('Expected target `rubric`.`id`.'))

        target_obj = self.get_rubric_by_id(target_id)
        if not (target_obj.attribute_mode == Rubric.ATTRIBUTE_IS_CHARACTERISTIC or target_obj.attribute_mode == Rubric.ATTRIBUTE_IS_MARK):
            raise CommandError(ugettext('Target `rubric`.`attribute_mode` is not "characteristic" or "mark".'))

        attrs = PublicationCharacteristicOrMark.objects.filter(rubric__exact=target_obj.id, publication__active=True).\
            exclude(value__in=target_obj.get_descendants(include_self=False).distinct().values_list('name', flat=True)).\
            distinct().order_by('value').values_list('value', flat=True)

        for attr in attrs:
            child = Facet(parent=target_obj, name=attr, slug=slugify(attr))
            child.save()