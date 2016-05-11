#-*- coding: utf-8 -*-
from haystack import indexes
from publication_backbone.models import Publication
from publication_backbone.plugins.text.models import TextItem
from publication_backbone.plugins.file.models import FileItem
from publication_backbone.plugins.picture.models import PictureItem
from django.template import loader, Context


class PublicationIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='name')
    sub_name = indexes.CharField(model_attr='sub_name', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    tags = indexes.CharField(model_attr='tags', null=True)
    author = indexes.CharField(model_attr='author', null=True)
    date_added = indexes.DateTimeField(model_attr='date_added')
    text = indexes.NgramField(document=True, use_template=True)

    def get_model(self):
        return Publication

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.active()

    def prepare(self, obj):
        """
        Fetches and adds/alters data before indexing.
        """
        data = super(PublicationIndex, self).prepare(obj)
        # get all text plugins
        try:
            text_contentitems = obj.content.contentitems.instance_of(TextItem)
        except:
            text_contentitems = []
        try:
            file_contentitems = obj.content.contentitems.instance_of(FileItem)
        except:
            file_contentitems = []
        try:
            picture_contentitems = obj.content.contentitems.instance_of(PictureItem)
        except:
            picture_contentitems = []
        t = loader.select_template(('search/indexes/publication_backbone/publication_text.txt', ))
        data['text'] = t.render(Context({'object': obj,
                                     'content_data': { 'text': text_contentitems, 'file': file_contentitems, 'picture': picture_contentitems }}))

        return data
