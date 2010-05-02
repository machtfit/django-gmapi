"""URL pattern for serving static media. Use only to DEBUG!

Add something like the following to the bottom of your urls.py:

from django.conf import settings
if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^media/gmapi/', include('gmapi.urls.media')),
    ) + urlpatterns
"""
import os
from django.conf import settings
from django.conf.urls.defaults import * # pylint: disable-msg=W0401,W0614


MEDIA_ROOT = getattr(settings, 'GMAPI_MEDIA_ROOT',
                     os.path.join(os.path.dirname(
                     os.path.dirname(os.path.abspath(__file__))),
                     'media'))


urlpatterns = patterns('',
    (r'(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': MEDIA_ROOT}),
)
