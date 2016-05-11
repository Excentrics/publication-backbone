
publication-backbone
===================

This is a stand-alone module, which provides a flexible,
scalable publications management system with flexible block content.
An example of a site where it works ``http://www.beladm.ru``

Installations
============

First install the module, preferably in a your project virtual environment::

    pip install https://github.com/Excentrics/publication-backbone.git

The main dependencies will be automatically installed.

Configuration
-------------

To have a standard setup with publication-backbone, use::

In ``settings.py``::

    STATICFILES_FINDERS = (
        ...
        'pipeline.finders.PipelineFinder',
        'compressor.finders.CompressorFinder',
        ...
    )

    INSTALLED_APPS += (
        ...
        # Required dependencies
        'sorl.thumbnail',
        'mptt',
        'parler',
        'polymorphic',
        'polymorphic_tree',

        # Contrib
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'django.contrib.sitemaps',

        # The Main apps
        'publication_backbone',
        'fluent_pages.pagetypes.fluentpage',
        'fluent_contents',
        'django_wysiwyg',

        # Optional other CMS page types
        'fluent_pages.pagetypes.redirectnode',

        # CSS and JS compressor, use for templates
        'compressor',

        # Settings store backend
        'constance',
        'constance.backends.database',

        # For admin
        'django_mptt_admin',
        'salmonella',

        # CKEditor
        'ckeditor',

        # Publication Backbone Plugins
        'publication_backbone.plugins.text',
        'publication_backbone.plugins.content_gap',
        'publication_backbone.plugins.snippet',
        'publication_backbone.plugins.yandex_map',
        'publication_backbone.plugins.file',
        'publication_backbone.plugins.picture',
        'publication_backbone.plugins.form_designer_plugin',
        'publication_backbone.plugins.promo',
        'publication_backbone.plugins.sub_menu',
        'publication_backbone.plugins.sitemap',
        'publication_backbone.interview',
        'publication_backbone.quiz',

        # Beautiful fields
        'beautiful_fields',

        # CSS and JS builder
        'twitter_bootstrap',
        'pipeline',

        # Additional fields
        'any_imagefield',
        'any_urlfield',

        # Django form designer
        'form_designer',

        # Search
        'publication_backbone.search.backends.haystack_backend',
        'haystack',
        'elasticstack',

        # Widget pages via django-fluent-contents
        'fluent_pages.pagetypes.fluentpage',
        'fluent_contents',
        'fluent_contents.plugins.text',
        'django_wysiwyg',

        # Optional other CMS page types
        'fluent_pages.pagetypes.redirectnode',
        ...
    )

    DJANGO_WYSIWYG_FLAVOR = "ckeditor"
    DJANGO_WYSIWYG_MEDIA_URL = STATIC_URL + "ckeditor/"

    CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'


    PIPELINE_COMPILERS = (
      'pipeline.compilers.less.LessCompiler',
      'pipeline.compilers.coffee.CoffeeScriptCompiler',
    )

    STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

    # Relative path to publication_backbone directory must be replace to yours
    if DEBUG:
        PIPELINE_LESS_ARGUMENTS = "-ru --source-map --include-path=../../../../../src/publicationbackbone/publication_backbone/:../../../../../lib/python2.7/site-packages/publication_backbone/:../../../../../lib/python2.7/site-packages/twitter_bootstrap/"
    else:
        PIPELINE_LESS_ARGUMENTS = "-ru --clean-css --compress --include-path=../../../../../lib/python2.7/site-packages/publication_backbone/:../../../../../lib/python2.7/site-packages/twitter_bootstrap/"

    PIPELINE_CSS = {
        'styles': {
            'source_filenames': (
                'src/less/styles.less',
            ),
            'output_filename': 'css/styles.css',
            'extra_context': {
                'media': 'screen',
            },
        },
    }

    PIPELINE_JS = {
        'bootstrap': {
            'source_filenames': (
              'twitter_bootstrap/js/transition.js',
              'twitter_bootstrap/js/alert.js',
              'twitter_bootstrap/js/button.js',
              'twitter_bootstrap/js/carousel.js',
              'twitter_bootstrap/js/collapse.js',
              'twitter_bootstrap/js/dropdown.js',
              'twitter_bootstrap/js/modal.js',
              'twitter_bootstrap/js/tooltip.js',
              'twitter_bootstrap/js/popover.js',
              'twitter_bootstrap/js/scrollspy.js',
              'twitter_bootstrap/js/tab.js',
              'twitter_bootstrap/js/affix.js',
            ),
            'output_filename': 'js/bootstrap.js',
        },
    }

    THUMBNAIL_ENGINE = 'publication_backbone.utils.sorl_pil_engine.Engine'

    FLUENT_PAGES_TEMPLATE_DIR = os.path.join(TEMPLATE_DIRS[0], 'pages')

    CKEDITOR_CONFIGS = {'default': {
        'toolbar': [
                    ['ShowBlocks'],
                    ['Cut', 'Copy', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'],
                    ['Find', 'Replace'],
                    ['Source', 'Maximize'],
                    '/',
                    ['Bold', 'Italic', 'Underline', 'Strike', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
                    ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
                    '/',
                    ['Format', 'Styles', 'Font', 'FontSize'],
                    ['TextColor', 'BGColor'],
                    ['Link', 'Unlink', 'Anchor'],
                    ['Table', 'HorizontalRule', 'SpecialChar', 'Iframe'],
                ],
        'skin': 'moono',
    }}

    CKEDITOR_UPLOAD_PATH = "uploads/"

    CKEDITOR_IMAGE_BACKEND = "pillow"

    CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'

    COMPRESS_OUTPUT_DIR = 'publication_backbone_cache'

    # haystack search settings _CHANGE_THIS_SETTINGS_TO_YOURS_SEARCH_ENGINE!
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': '<index_name>',
        }
    }

    PUBLICATION_BACKBONE_SEARCH_BACKENDS = [
        'publication_backbone.search.backends.haystack_backend.haystack_search.HaystackSearchBackend',
    ]

    HAYSTACK_SEARCH_RESULTS_PER_PAGE = 15
    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

    CONSTANCE_CONFIG = {
        'META_CONTAINER': ("", _("Meta block")),
        'COUNTERS': ("", _("External counters code (put into block after body tag (do not use image)")),
    }


In ``urls.py``::
    ...
    from django.contrib import admin
    from django.contrib.sites.models import Site
    from django.views.generic import TemplateView

    urlpatterns += patterns('',
        url(r'^robots.txt$',
           TemplateView.as_view(template_name='robots.txt',
                                content_type='text/plain',
                                get_context_data=lambda: {'domain': Site.objects.get_current().domain},),
           name='robots.txt'),
        url(r'^', include('publication_backbone.sitemap.urls'), name='sitemap'),
        url(r'^admin/salmonella/', include('salmonella.urls')),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('publication_backbone.urls')),
        url(r'', include('fluent_pages.urls')),
    )
    ...

Addition
--------

In the folder ``additional`` , you can find the necessary to your project directory ``static``, ``templates``
and ``locale``. Without this folders your project will not work. Just copy them to the root of your project.
