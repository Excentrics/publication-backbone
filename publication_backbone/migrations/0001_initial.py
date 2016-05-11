# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import sorl.thumbnail.fields
import mptt.fields
import bitfield.models
from django.db import models, migrations
from publication_backbone.utils.media import get_media_path
from publication_backbone.models_bases.polymorphic_mptt.models import PolymorphicTreeForeignKey
from publication_backbone.models_bases.publication import on_publication_group_delete
from publication_backbone.models_bases.mixins import PlaceholderImageMixin, PolymorphicModelMixin
from publication_backbone.models_bases.category import RubricMixIn, LinkMixIn
from publication_backbone.utils.validators import URLOrAbsolutePathValidator
from publication_backbone.models_bases.rubricator import (DeterminantFilteringMixin,
                                                          FacetFilteringMixin,
                                                          HierarchyMixIn,
                                                          FacetMixIn,
                                                          DeterminantMixIn)



class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('slug', models.SlugField(help_text='Used for URLs, auto-generated from name if blank', verbose_name='slug')),
                ('creation_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='creation date', editable=False, db_index=True)),
                ('visible', models.BooleanField(default=False, db_index=True, verbose_name='visible')),
                ('path', models.CharField(verbose_name='path', unique=True, max_length=255, editable=False, db_index=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'base category',
                'verbose_name_plural': 'base categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rubric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', models.SlugField(help_text='Used for URLs, auto-generated from name if blank', verbose_name='slug')),
                ('path', models.CharField(verbose_name='path', unique=True, max_length=255, editable=False, db_index=True)),
                ('creation_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='creation date', editable=False, db_index=True)),
                ('display_mode', models.PositiveSmallIntegerField(default=10, verbose_name='display mode', choices=[(10, 'standard'), (20, 'show extra'), (30, 'show collapsed')])),
                ('active', models.BooleanField(default=True, db_index=True, verbose_name='active')),
                ('attribute_mode', models.PositiveSmallIntegerField(default=0, help_text='Specifying mode of getting attributes for publication', db_index=True, verbose_name='attribute mode', choices=[(0, 'none'), (10, 'is characteristic'), (20, 'is mark'), (30, 'is relation')])),
                ('tags', models.CharField(help_text='Space delimited tags, for example: "red strikethrough"', max_length=255, null=True, verbose_name='tags', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('system_flags', bitfield.models.BitField([(b'delete_restriction', 'Delete restriction'), (b'change_parent_restriction', 'Change parent restriction'), (b'change_slug_restriction', 'Change slug restriction'), (b'change_subclass_restriction', 'Change subclass restriction'), (b'has_child_restriction', 'Has child restriction'), (b'tagged_restriction', 'Tagged restriction')], default=None, null=True, verbose_name='system flags')),
                ('image', sorl.thumbnail.fields.ImageField(upload_to=get_media_path, verbose_name='image', blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'rubric',
                'verbose_name_plural': 'publication rubricator',
            },
            bases=(DeterminantFilteringMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Hierarchy',
            fields=[
                ('rubric_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='publication_backbone.Rubric')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'hierarchy',
                'verbose_name_plural': 'hierarchy rubricator',
            },
            bases=(FacetFilteringMixin, HierarchyMixIn, 'publication_backbone.rubric'),
        ),
        migrations.CreateModel(
            name='Facet',
            fields=[
                ('rubric_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='publication_backbone.Rubric')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'facet',
                'verbose_name_plural': 'facet rubricator',
            },
            bases=(FacetFilteringMixin, FacetMixIn, 'publication_backbone.rubric'),
        ),
        migrations.CreateModel(
            name='Determinant',
            fields=[
                ('rubric_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='publication_backbone.Rubric')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'determinant',
                'verbose_name_plural': 'determinant rubricator',
            },
            bases=(DeterminantMixIn, 'publication_backbone.rubric'),
        ),
         migrations.CreateModel(
            name='Category',
            fields=[
                ('basecategory_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='publication_backbone.BaseCategory')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'category',
                'verbose_name_plural': 'publication categories',
            },
            bases=('publication_backbone.basecategory',),
        ),
        migrations.CreateModel(
            name='CategoryDivider',
            fields=[
                ('basecategory_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='publication_backbone.BaseCategory')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'divider',
                'verbose_name_plural': 'categories dividers',
            },
            bases=('publication_backbone.basecategory',),
        ),
        migrations.CreateModel(
            name='CategoryLink',
            fields=[
                ('basecategory_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='publication_backbone.BaseCategory')),
                ('url', models.CharField(help_text='Universal Resource Locator', max_length=200, verbose_name='URL', validators=[URLOrAbsolutePathValidator()])),
            ],
            options={
                'abstract': False,
                'verbose_name': 'link',
                'verbose_name_plural': 'links',
            },
            bases=('publication_backbone.basecategory', ),
        ),
        migrations.CreateModel(
            name='CategoryPublicationRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation_direction', models.CharField(default=b'b', help_text='Defines the direction of relation on which selection is carried out', max_length=1, verbose_name='relation direction', choices=[(b'b', 'bidirectional'), (b'f', 'forward'), (b'r', 'reverse')])),
                ('category', mptt.fields.TreeForeignKey(related_name='publication_relations', verbose_name='category', to='publication_backbone.Category')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'category publication relation',
                'verbose_name_plural': 'category publication relations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', models.SlugField(help_text='For use into URL', unique=True, verbose_name='slug')),
                ('active', models.BooleanField(default=False, help_text='If this flag disable the publication not show anywhere', verbose_name='active')),
                ('grp', models.CharField(verbose_name='coalesce group id', max_length=255, editable=False, db_index=True)),
                ('date_added', models.DateTimeField(default=datetime.datetime.now, verbose_name='date added')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(help_text='This image used in publication list as main image of publication', upload_to=get_media_path, verbose_name='image', blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'publication',
                'verbose_name_plural': 'Publications',
            },
            bases=(PlaceholderImageMixin, PolymorphicModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PublicationCharacteristicOrMark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255, verbose_name='value')),
                ('tags', models.CharField(help_text='Space delimited tags, for example: "red strikethrough"', max_length=255, null=True, verbose_name='tags', blank=True)),
                ('publication', models.ForeignKey(related_name='additional_characteristics_or_marks', verbose_name='publication', to='publication_backbone.Publication')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'additional publication charsc or mark',
                'verbose_name_plural': 'additional publication chars or marks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PublicationGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('date_added', models.DateTimeField(default=datetime.datetime.now, verbose_name='Date added')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last modified')),
                ('image', sorl.thumbnail.fields.ImageField(upload_to=get_media_path, verbose_name='image', blank=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_publication_backbone.publicationgroup_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'publication group',
                'verbose_name_plural': 'publication groups',
            },
            bases=(PlaceholderImageMixin, PolymorphicModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PublicationImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', sorl.thumbnail.fields.ImageField(upload_to=get_media_path, max_length=200, verbose_name='Picture')),
                ('caption', models.CharField(max_length=100, null=True, verbose_name='Optional caption', blank=True)),
                ('sort', models.IntegerField(default=0, verbose_name='Sort Order')),
                ('publication', models.ForeignKey(related_name='images', to='publication_backbone.Publication')),
            ],
            options={
                'ordering': ('sort',),
                'abstract': False,
                'verbose_name': 'publication image',
                'verbose_name_plural': 'publication images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PublicationRelatedCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.CharField(default=b'date_added_asc', max_length=255, verbose_name='Display Order', blank=True, choices=[(b'date_added_asc', 'Date Added: old first'), (b'date_added_desc', 'Date Added: new first'), (b'name_desc', 'Alphabetical: descending'), (b'name_asc', 'Alphabetical')])),
                ('category', mptt.fields.TreeForeignKey(related_name='+', verbose_name='category', to='publication_backbone.Category')),
                ('publication', models.ForeignKey(related_name='related_categories', to='publication_backbone.Publication')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'publication related category',
                'verbose_name_plural': 'publication related categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PublicationRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_publication', models.ForeignKey(related_name='forward_relations', verbose_name='from publication', to='publication_backbone.Publication')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'publication relation',
                'verbose_name_plural': 'publication relations',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='rubric',
            name='parent',
            field=PolymorphicTreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='publication_backbone.Rubric', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rubric',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_publication_backbone.rubric_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publicationrelation',
            name='rubric',
            field=mptt.fields.TreeForeignKey(related_name='+', verbose_name='rubric', to='publication_backbone.Rubric'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publicationrelation',
            name='to_publication',
            field=models.ForeignKey(related_name='backward_relations', verbose_name='to publication', to='publication_backbone.Publication'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='publicationrelation',
            unique_together=set([('from_publication', 'to_publication', 'rubric')]),
        ),
        migrations.AlterUniqueTogether(
            name='publicationrelatedcategory',
            unique_together=set([('publication', 'category')]),
        ),
        migrations.AddField(
            model_name='publicationcharacteristicormark',
            name='rubric',
            field=mptt.fields.TreeForeignKey(related_name='publication_additional_characteristics_or_marks', verbose_name='rubric', to='publication_backbone.Rubric'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='publicationcharacteristicormark',
            unique_together=set([('publication', 'rubric')]),
        ),
        migrations.AddField(
            model_name='publication',
            name='group',
            field=models.ForeignKey(related_name='publications', on_delete=on_publication_group_delete, verbose_name='group', blank=True, to='publication_backbone.PublicationGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_publication_backbone.publication_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='rubrics',
            field=mptt.fields.TreeManyToManyField(help_text='Use "ctrl" key for choose multiple rubrics', to='publication_backbone.Rubric', verbose_name='rubrics', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='categorypublicationrelation',
            name='rubric',
            field=mptt.fields.TreeForeignKey(related_name='+', verbose_name='relation', to='publication_backbone.Rubric', help_text='Defines the relation using for filtering'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecategory',
            name='parent',
            field=PolymorphicTreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='publication_backbone.BaseCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecategory',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_publication_backbone.basecategory_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='rubrics',
            field=mptt.fields.TreeManyToManyField(to='publication_backbone.Rubric', verbose_name='rubrics', blank=True),
            preserve_default=True,
        ),
    ]
