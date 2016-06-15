#!/bin/env python
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import os
import sys


class osx_install_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}

packages, data_files = [], []

def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

for module in ("publication_backbone",):
    for dirpath, dirnames, filenames in os.walk(module):
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'): del dirnames[i]
        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
        elif filenames:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


import datetime, time
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
version = '0.6.6.0-' + st


setup(
    name='PublicationBackbone',
    version=version,
    author='Excentrics LLC',
    author_email='info@excentrics.ru',
    packages=packages,
    data_files=data_files,
    cmdclass=cmdclasses,
    scripts=[],
    url='https://github.com/Excentrics/publication-backbone.git',
    license='LICENSE.txt',
    description='Publication Backbone.',
    long_description=open('README.md').read(),
    install_requires=[
        "Pillow",
        "Django == 1.7.10",
        "pytils",
        "lxml == 3.3.4",
        "django-mptt == 0.7.4",
        "git+git://github.com/mbraak/django-mptt-admin.git",
        "django-polymorphic == 0.7.2",
        "django-haystack == 2.4.1",
        "pyelasticsearch == 1.4",
        "elasticsearch == 1.9.0",
        "elasticstack == 0.4.0",
        "django-salmonella == 0.6.1",
        "django-constance == 1.1.1",
        "django-picklefield == 0.3.1",
        "django_compressor == 1.4",
        "django-constance == 1.0.1",
        "django-ckeditor == 4.4.6",
        "git+git://github.com/bradleyayers/django-ace.git",
        "git+git://github.com/Excentrics/beautiful-fields.git",
        "git+git://github.com/disqus/django-bitfield.git",
        "git+git://github.com/sergey-romanov/django-form-designer.git",
        "git+git://github.com/sergey-romanov/django-mptt-admin.git",
        "sorl-thumbnail == 12.3",
        "django-classy-tags == 0.6.2",
        "django-simple-captcha",
        "django-wysiwyg == 0.7.1",
        "git+git://github.com/edoburu/django-fluent-pages.git",
        "django-fluent-contents==1.0.2",
        "django-twitter-bootstrap==3.1.1",
        "django-pipeline==1.3.23",
        "django_compressor==1.4",
        "django-any-urlfield",
        "django-any-imagefield",
        "git+git://github.com/SmartTeleMax/chakert.git",
    ],
)