#-*- coding: utf-8 -*-


from django.core.management.base import NoArgsCommand, CommandError

from optparse import make_option

from publication_backbone.models import Publication

from django.utils.translation import ugettext


class Command(NoArgsCommand):
    help = ugettext("Set rubrics for publication by it's additional attributes.")

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--publication',
            dest='publication_id',
            type=long,
            default=None,
            help=ugettext('Publication id')
        ),
    )

    def get_publication_by_id(self, id):
        """
        Get publication by id
        """
        try:
            return Publication.objects.get(pk=id)
        except Publication.DoesNotExist:
            raise CommandError(ugettext('No %(model)s matches the given `id`=`%(id)s`.') % {
                'model': Publication._meta.object_name,
                'id': id})

    def get_rubric_by_attribute(self, attribute):
        """
        Get rubric for additional attribute:
            find first descendant for attribute.rubric with name = attribute.value
            return only first rubric (may be several rubrics match this query)
        """
        try:
            rubrics = attribute.rubric.get_descendants().filter(name=attribute.value)[:1]
            return rubrics[0] if rubrics else None
        except:
            return None

    def handle_noargs(self, **options):
        publication_id = options.get('publication_id')
        if publication_id is None:
            raise CommandError(ugettext('Expected publication `publication`.`id`.'))
        # get publication and additional attributes
        publication = self.get_publication_by_id(publication_id)
        attributes = publication.additional_characteristics_or_marks.all()
        for attr in attributes:
            # try to find rubric for additional attr value
            rubric = self.get_rubric_by_attribute(attr)
            if rubric:
                # add this rubric to publication
                try:
                    publication.rubrics.add(rubric)
                    publication.save()
                except:
                    # if cant add attribute raise error
                    raise CommandError(ugettext('Cant add rubric with id=%(rubric_id)s to publication id = %(publication_id)s.') %
                                       {'rubric_id': rubric.pk,
                                        'publication_id': publication.pk})

                # delete additional attribute
                try:
                    attr.delete()
                except:
                    # if cant delete attribute raise error
                    raise CommandError(ugettext('Cant delete additional attribute with id = %s to rubric with id=%(rubric_id).') % attr.pk,)

