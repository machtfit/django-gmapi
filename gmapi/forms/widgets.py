"""Custom Map widget."""
from django.conf import settings
from django.forms.util import flatatt
from django.forms.widgets import Widget
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.simplejson import dumps
from gmapi import maps


MAPS_URL = getattr(settings, 'GMAPI_MAPS_URL',
                     'http://maps.google.com/maps/api/js?sensor=false')

# Same rules apply as ADMIN_MEDIA_PREFIX.
# The default will have MEDIA_URL prepended later.
MEDIA_PREFIX = getattr(settings, 'GMAPI_MEDIA_PREFIX', 'gmapi/')


class GoogleMap(Widget):
    def render(self, name, value, attrs=None):
        if value is None:
            value = maps.Map()
        default_attrs = {'id': name, 'class': 'gmap'}
        if attrs:
            default_attrs.update(attrs)
        final_attrs = self.build_attrs(default_attrs)
        width = final_attrs.pop('width', 500)
        height = final_attrs.pop('height', 400)
        style = (u'position:relative;width:%dpx;height:%dpx;' %
                 (width, height))
        final_attrs['style'] = style + final_attrs.get('style', '')
        map_div = (u'<div class="%s" style="position:absolute;'
                   u'width:%dpx;height:%dpx"></div>' %
                   (escape(dumps(value, separators=(',', ':'))),
                    width, height))
        map_img = (u'<img style="position:absolute;z-index:1" '
                   u'width="%(x)d" height="%(y)d" alt="Google Map" '
                   u'src="%(map)s&size=%(x)dx%(y)d" />' %
                   {'map': escape(value), 'x': width, 'y': height})
        return mark_safe(u'<div%s>%s%s</div>' %
                         (flatatt(final_attrs), map_div, map_img))

    class Media:
        js = (MAPS_URL, '%sjs/jquery.gmapi%s.js' %
              (MEDIA_PREFIX, ('' if settings.DEBUG else '.min')))
