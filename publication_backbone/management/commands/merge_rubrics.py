#-*- coding: utf-8 -*-
"""
``merge_rubrics``
---------------------

``merge_rubrics`` - merge two rubrics in one.
"""

from django.core.management.base import NoArgsCommand, CommandError

from optparse import make_option

from publication_backbone.models import Rubric, Publication, Category, PublicationCharacteristicOrMark

from django.utils.translation import ugettext


class Command(NoArgsCommand):
    help = ugettext("Merge two rubrics in one.")

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--to',
            dest='to_id',
            type=long,
            default=None,
            help=ugettext('Destination rubric id')
        ),
        make_option(
            '--from',
            dest='from_id',
            type=long,
            default=None,
            help=ugettext('Source rubric id')
        ),
    )

    def get_rubric_by_id(self, id):
        try:
            return Rubric.objects.get(pk=id)
        except Rubric.DoesNotExist:
            raise CommandError(ugettext('No %(model)s matches the given `id`=`%(id)d`.') % {
                'model': Rubric._meta.object_name,
                'id': id})

    def handle_noargs(self, **options):
        to_id, from_id = options.get('to_id'), options.get('from_id')
        if to_id is None:
            raise CommandError(ugettext('Expected destination `rubric`.`id`.'))
        if from_id is None:
            raise CommandError(ugettext('Expected source `rubric`.`id`.'))
        if to_id == from_id:
            raise CommandError(ugettext("Can't merge `rubric` with itself."))

        to_obj, from_obj = self.get_rubric_by_id(to_id), self.get_rubric_by_id(from_id)

        if from_obj.system_flags.delete_restriction:
            raise CommandError(from_obj.system_flags.get_label('delete_restriction'))

        tree_opts = Rubric._mptt_meta
        if getattr(to_obj, tree_opts.tree_id_attr) == getattr(from_obj, tree_opts.tree_id_attr) and \
                        getattr(to_obj, tree_opts.left_attr) > getattr(from_obj, tree_opts.left_attr) and \
                        getattr(to_obj, tree_opts.right_attr) < getattr(from_obj, tree_opts.right_attr):
            raise CommandError(ugettext("A destination `rubric` may not be made a child of any of its descendants."))

        # Update related rubrics
        child_of_from_obj = from_obj.get_children()
        for child in child_of_from_obj:
            child.move_to(to_obj, 'last-child')
            child.save()
            to_obj = self.get_rubric_by_id(to_obj.id)

        # Update related publications
        Publication.rubrics.through.objects.filter(rubric__exact=from_obj.id).update(rubric=to_obj.id)

        # Update related publication attributes
        PublicationCharacteristicOrMark.objects.filter(rubric__exact=from_obj.id).update(rubric=to_obj.id)

        # Update related categories
        Category.rubrics.through.objects.filter(rubric__exact=from_obj.id).update(rubric=to_obj.id)

        to_obj.active = to_obj.active or from_obj.active

        if to_obj.attribute_mode != Rubric.ATTRIBUTE_IS_CHARACTERISTIC and from_obj.attribute_mode == Rubric.ATTRIBUTE_IS_CHARACTERISTIC:
            to_obj.attribute_mode = Rubric.ATTRIBUTE_IS_CHARACTERISTIC

        to_obj.save()

        from_obj.delete()