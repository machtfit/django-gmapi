"""Template tags for loading necessary javascript libraries."""
from django import template
from django.conf import settings
from django.http import urlencode
from django.utils.encoding import iri_to_uri
from django.utils.simplejson import dumps


register = template.Library()


JSAPI_URL = getattr(settings, 'GMAPI_JSAPI_URL',
                    'http://www.google.com/jsapi')

# By default, auto-load Maps v3.
JSAPI_AUTOLOAD = getattr(settings, 'GMAPI_JSAPI_AUTOLOAD',
                         {'modules':
                          [{'name': 'maps',
                            'version': '3',
                            'other_params':
                            'sensor=false'}]})

# Not needed with v3 of Maps.
JSAPI_KEY = getattr(settings, 'GMAPI_JSAPI_KEY', '')


@register.inclusion_tag('gmapi/script_tag.html')
def gmapi_jsapi(extra_autoload=None):
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

    # Build autoload dict.
    autoload = {}
    if JSAPI_AUTOLOAD:
        for module in JSAPI_AUTOLOAD.get('modules', []):
            autoload.setdefault('modules', []).append(module)
    if extra_autoload:
        for module in extra_autoload.get('modules', []):
            autoload.setdefault('modules', []).append(module)

    # Compile parameters.
    params = {}
    if autoload:
        params['autoload'] = dumps(autoload, separators=(',', ':'))
    if JSAPI_KEY:
        params['key'] = JSAPI_KEY
    return {'url': iri_to_uri(JSAPI_URL), 'params': urlencode(params)}


# Load the uncompressed version if DEBUG is enabled.
JQUERY_PLUGINS = getattr(settings, 'GMAPI_JQUERY_PLUGINS',
                         ['%sgmapi/js/jquery.gmapi%s.js' %
                          (settings.MEDIA_URL,
                           '.min' if not settings.DEBUG else '')])

# Default to latest version of jQuery 1.4.
JQUERY_VERSION = getattr(settings, 'GMAPI_JQUERY_VERSION', '1.4')


@register.inclusion_tag('gmapi/script_tag.html')
def gmapi_jquery(callback=None, extra_plugins=None, jquery=None):
    """Insert <script> tag for loading jQuery with Google AJAX API loader.

    Supports dynamically loading jQuery plugins by calling getScript on
    each plugin specified. A single callback function will be called
    once all scripts have been loaded.

    You can also specify an existing instance of jQuery if it's already
    loaded.
    """

    # Build list of plugins.
    plugins = []
    if JQUERY_PLUGINS:
        plugins += JQUERY_PLUGINS
    if extra_plugins:
        plugins += (extra_plugins if hasattr(extra_plugins, '__iter__')
                    else [extra_plugins])

    # Build plugin loading script.
    plugin_script = ''
    if plugins:
        if callback:
            if len(plugins) > 1:
                # Handle multiple plugins.
                plugin_script += ("    var i = 1; var j = %d;\n"
                                  "    var x = function(){\n"
                                  "        if (i++ == j) (%s)();\n"
                                  "    };\n" % (len(plugins), callback))
                callback = ', x'
            else:
                callback = ', %s' % callback
        for url in plugins:
            # User jQuery to load each plugin.
            plugin_script += ("    jQuery.getScript('%s'%s);\n" %
                              (url, callback or ''))
        # Wrap entire thing in an anonymous function.
        plugin_script = "function(){\n%s}" % plugin_script

    # Compile script.
    script = ''
    if not jquery:
        # Load the uncompressed version if DEBUG is enabled.
        debug = ", {uncompressed:true}" if settings.DEBUG else ''
        # Load jQuery.
        script += "google.load('jquery', '%s'%s);" % (JQUERY_VERSION, debug)
        # Load plugins or callback.
        if plugin_script or callback:
            script += ("\ngoogle.setOnLoadCallback(%s);" %
                       (plugin_script or callback))
    elif plugin_script or callback:
        if jquery not in ('jQuery', 'window.jQuery'):
            # Reassign back to what we expect it to be called.
            # E.g. Django Admin moves it to django.jQuery.
            script += "window.jQuery = %s;\n" % jquery
        # Load plugins or callback on document ready event.
        script += "jQuery(%s);" % (plugin_script or callback)

    # Send script to template.
    return {'script': script}
