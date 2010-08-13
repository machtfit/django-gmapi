"""URL pattern for serving static media. Use only to DEBUG!

Add something like the following to the bottom of your urls.py:

from django.conf import settings
if settings.DEBUG:
    urlpatterns = patterns('',
        (r'', include('gmapi.urls.media')),
    ) + urlpatterns
"""
from os import path
from django.conf import settings
from django.conf.urls.defaults import *
from urlparse import urljoin


# Same rules apply as regular MEDIA_ROOT.
MEDIA_ROOT = getattr(settings, 'GMAPI_MEDIA_ROOT',
                     path.abspath(path.join(path.dirname(
                     path.dirname(__file__)), 'media', 'gmapi')))

# Same rules apply as ADMIN_MEDIA_PREFIX.
MEDIA_PREFIX = getattr(settings, 'GMAPI_MEDIA_PREFIX',
                       urljoin(settings.MEDIA_URL, 'gmapi/').lstrip('/'))


urlpatterns = []


if not (MEDIA_PREFIX.startswith(u'http://') or
        MEDIA_PREFIX.startswith(u'https://')):
    urlpatterns = patterns('',
        (r'^%s(?P<path>.*)$' % MEDIA_PREFIX, 'django.views.static.serve',
         {'document_root': MEDIA_ROOT}),
    )
