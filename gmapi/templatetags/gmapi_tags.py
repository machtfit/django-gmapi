"""Template tags for loading necessary javascript libraries."""
from django import template
from django.conf import settings
from django.http import urlencode
from django.utils.encoding import iri_to_uri
from django.utils.simplejson import dumps


register = template.Library()


JSAPI_URL = getattr(settings, 'GOOGLE_JSAPI_URL',
                    'http://www.google.com/jsapi')

# By default, auto-load Maps v3.
JSAPI_AUTOLOAD = getattr(settings, 'GOOGLE_JSAPI_AUTOLOAD',
                         {'modules':
                          [{'name': 'maps',
                            'version': '3',
                            'other_params':
                            'sensor=false'}]})

# Not needed with v3 of Maps.
JSAPI_KEY = getattr(settings, 'GOOGLE_JSAPI_KEY', '')


@register.inclusion_tag('gmapi/script_tag.html')
def google_jsapi(autoload=JSAPI_AUTOLOAD):
    """Insert <script> tag for Google AJAX API loader.

    Supports auto-loading APIs which effectively does a server side include
    for the specified APIs, reducing network connections. See
    http://code.google.com/apis/ajax/documentation/#AutoLoading for
    syntax.

    Note: In my experiments, auto-loading 3rd party APIs such as jQuery
    causes Google APIs to revert to a simple google.load(), which doesn't
    actually reduce network connections at all. So I only auto-load
    Google APIs and use google.load() manually for any 3rd party APIs.
    """
    params = {}
    if autoload:
        params['autoload'] = dumps(autoload, separators=(',', ':'))
    if JSAPI_KEY:
        params['key'] = JSAPI_KEY
    return {'url': iri_to_uri(JSAPI_URL), 'params': urlencode(params)}


# Load the uncompressed version if DEBUG is enabled.
JSAPI_JQ_PLUGINS = getattr(settings, 'GOOGLE_JSAPI_JQ_PLUGINS',
                           ['%sgmapi/js/jquery.gmapi%s.js' %
                            (settings.MEDIA_URL,
                             '.min' if not settings.DEBUG else '')])

# Default to latest version of jQuery 1.4.
JSAPI_JQ_VERSION = getattr(settings, 'GOOGLE_JSAPI_JQ_VERSION', '1.4')


@register.inclusion_tag('gmapi/script_tag.html')
def google_jsapi_jquery(callback=None, plugins=JSAPI_JQ_PLUGINS):
    """Insert <script> tag for loading jQuery with Google AJAX API loader.

    Supports dynamically loading jQuery plugins by calling getScript on
    each plugin specified. A single callback function will be called
    once all scripts have been loaded.
    """
    # Load the uncompressed version if DEBUG is enabled.
    script = "google.load('jquery', '%s'%s);" % (JSAPI_JQ_VERSION,
                                                 ", {uncompressed:true}"
                                                 if settings.DEBUG else '')
    if plugins:
        # Handle a single plugin or a list of plugins.
        if isinstance(plugins, basestring):
            plugins = [plugins]
        script += "\ngoogle.setOnLoadCallback(function(){\n"
        if callback and len(plugins) > 1:
            script += ("    var i = 1; var j = %d;\n"
                       "    var callback = function(){\n"
                       "        if (i++ == j) %s();\n"
                       "    };\n" % (len(plugins), callback))
            callback = 'callback'
        for url in plugins:
            script += ("    jQuery.getScript('%s'%s);\n"
                       % (url, (', ' + callback) if callback else ''))
        script += "});"
    return {'script': script}
