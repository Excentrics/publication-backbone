"""
Tools for sending email.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.core.mail.message import EmailMultiAlternatives


def get_connection(backend=None, fail_silently=False, **kwds):
    path = backend or settings.EMAIL_BACKEND
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing email backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass(fail_silently=fail_silently, **kwds)


def send_mail(subject, message, from_email, recipient_list, html_message=None,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list,
                        connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')
    mail.send(fail_silently=fail_silently)
