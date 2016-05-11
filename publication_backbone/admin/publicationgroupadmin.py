#-*- coding: utf-8 -*-
from django.contrib import admin
from publication_backbone.models import PublicationGroup


class PublicationGroupAdmin(admin.ModelAdmin):

    save_on_top = True

    list_display = ('name', 'slug', 'date_added', 'last_modified',)

    search_fields = ['name', 'slug', ]

    prepopulated_fields = {"slug": ("name",)}


if not PublicationGroup in admin.site._registry:
    admin.site.register(PublicationGroup, PublicationGroupAdmin)
