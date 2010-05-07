# pylint: disable-msg=C0103
"""Implements the Google Maps API v3."""
import time
import urllib
from django.conf import settings
from django.core.cache import cache
from django.http import urlencode
from django.utils.encoding import force_unicode, smart_str
from django.utils.simplejson import loads


STATIC_URL = getattr(settings, 'GMAPI_STATIC_URL',
                     'http://maps.google.com/maps/api/staticmap')

GEOCODE_URL = getattr(settings, 'GMAPI_GEOCODE_URL',
                      'http://maps.google.com/maps/api/geocode')


class MapClass(dict):
    """A base class for Google Maps API classes.

    Handles string conversion so that we only have to define a
    __unicode__ method.
    """
    def __str__(self):
        if hasattr(self, '__unicode__'):
            return force_unicode(self).encode('utf-8')
        return '%s object' % self.__class__.__name__


class MapConstant(MapClass):
    """A custom constant class.

    For holding special Google Maps constants. When parsed by
    JSONEncoder and subsequently by our custom jQuery plugin,
    it will be converted to the actual constant value.

    """
    def __init__(self, cls, const):
        super(MapConstant, self).__init__(val='%s.%s' % (cls, const))
        self.const = const

    def __setitem__(self, key, value):
        raise KeyError, key

    def __unicode__(self):
        return self.const.lower()


class MapConstantClass(object):
    """A custom factory class for constants."""
    def __init__(self, name, constants):
        for const in constants:
            setattr(self, const, MapConstant(name, const))


class Map(MapClass):
    """A Google Map.

    Equivalent to google.maps.Map. When parsed by JSONEncoder
    and subsequently by our custom jQuery plugin, it will be
    converted to an actual google.maps.Map instance.

    """
    def __init__(self, mapDiv=None, opts=None):
        """mapDiv is not used."""
        super(Map, self).__init__(cls='Map')
        self['arg'] = Args(['mapDiv', 'opts'], ['div'])
        self.setOptions(opts)

    def __unicode__(self):
        """Produces a static map image url.

        Don't forget to set the map option 'size' (as an instance
        of maps.Size). Or alternatively you can append it to the
        resulting string (e.g. '&size=400x400').

        """
        opts = self['arg'].get('opts', {})
        params = {}
        for p in ['center', 'zoom', 'size', 'format', 'language']:
            if p in opts:
                params[p] = unicode(opts[p])
        if 'mapTypeId' in opts:
            params['maptype'] = unicode(opts['mapTypeId'])
        if 'mobile' in opts:
            params['mobile'] = 'true' if opts['mobile'] else 'false'
        if 'visible' in opts:
            params['visible'] = '|'.join([unicode(v) for v in opts['visible']])
        if 'mkr' in self:
            params['markers'] = [unicode(m) for m in self['mkr']]
        params['sensor'] = 'true' if opts.get('sensor') else 'false'
        return u'%s?%s' % (STATIC_URL, urlencode(params, doseq=True))

    def fitBounds(self, bounds):
        raise NotImplementedError

    def getBounds(self):
        raise NotImplementedError

    def getCenter(self):
        return self['arg'].get('opts', {}).get('center')

    def getDiv(self):
        raise NotImplementedError

    def getMapTypeId(self):
        return self['arg'].get('opts', {}).get('mapTypeId')

    def getZoom(self):
        return self['arg'].get('opts', {}).get('zoom')

    def setCenter(self, latlng):
        self.setOptions({'center': latlng})

    def setMapTypeId(self, mapTypeId):
        self.setOptions({'mapTypeId': mapTypeId})

    def setOptions(self, options):
        if options:
            self['arg'].setdefault('opts', {}).update(options)

    def setZoom(self, zoom):
        self.setOptions({'zoom': zoom})


MapTypeId = MapConstantClass('MapTypeId',
                             ('HYBRID', 'ROADMAP', 'SATELLITE', 'TERRAIN',))


MapTypeControlStyle = MapConstantClass('MapTypeControlStyle',
                                       ('DEFAULT', 'DROPDOWN_MENU',
                                        'HORIZONTAL_BAR',))


NavigationControlStyle = MapConstantClass('NavigationControlStyle',
                                          ('ANDROID', 'DEFAULT', 'SMALL',
                                           'ZOOM_PAN',))


ScaleControlStyle = MapConstantClass('ScaleControlStyle', ('DEFAULT',))


ControlPosition = MapConstantClass('ControlPosition',
                                   ('BOTTOM', 'BOTTOM_LEFT', 'BOTTOM_RIGHT',
                                    'LEFT', 'RIGHT', 'TOP', 'TOP_LEFT',
                                    'TOP_RIGHT',))


class Marker(MapClass):
    """A Google Marker.

    Equivalent to google.maps.Marker. When parsed by JSONEncoder
    and subsequently by our custom jQuery plugin, it will be
    converted to an actual google.maps.Map instance.

    """
    def __init__(self, opts=None):
        super(Marker, self).__init__(cls='Marker')
        self._map = None
        self['arg'] = Args(['opts'])
        self.setOptions(opts)

    def __unicode__(self):
        opts = self['arg'].get('opts', {})
        params = []
        for p in ['size', 'color', 'label', 'icon']:
            if p in opts:
                params.append('%s:%s' % (p, opts[p]))
        if 'shadow' in opts:
            params.append('shadow:%s' % 'true' if opts['shadow'] else 'false')
        if 'position' in opts:
            params.append(unicode(opts['position']))
        return '|'.join(params)

    def getClickable(self):
        return self['arg'].get('opts', {}).get('clickable')

    def getCursor(self):
        return self['arg'].get('opts', {}).get('cursor')

    def getDraggable(self):
        return self['arg'].get('opts', {}).get('draggable')

    def getFlat(self):
        return self['arg'].get('opts', {}).get('flat')

    def getIcon(self):
        return self['arg'].get('opts', {}).get('icon')

    def getMap(self):
        return self._map

    def getPosition(self):
        return self['arg'].get('opts', {}).get('position')

    def getShadow(self):
        return self['arg'].get('opts', {}).get('shadow')

    def getShape(self):
        return self['arg'].get('opts', {}).get('shape')

    def getTitle(self):
        return self['arg'].get('opts', {}).get('title')

    def getVisible(self):
        return self['arg'].get('opts', {}).get('visible')

    def getZIndex(self):
        return self['arg'].get('opts', {}).get('zIndex')

    def setClickable(self, flag):
        self.setOptions({'clickable': flag})

    def setCursor(self, cursor):
        self.setOptions({'cursor': cursor})

    def setDraggable(self, flag):
        self.setOptions({'draggable': flag})

    def setFlat(self, flag):
        self.setOptions({'flat': flag})

    def setIcon(self, icon):
        self.setOptions({'icon': icon})

    def setMap(self, gmap):
        self.setOptions({'map': gmap})

    def setOptions(self, options):
        if options and 'map' in options:
            if self._map:
                # Remove this marker from the map.
                self._map['mkr'].remove(self)
            # Save new map reference.
            self._map = options.pop('map')
            if self._map:
                # Add this marker to the map.
                self._map.setdefault('mkr', []).append(self)
        if options:
            self['arg'].setdefault('opts', {}).update(options)

    def setPosition(self, latlng):
        self.setOptions({'position': latlng})

    def setShadow(self, shadow):
        self.setOptions({'shadow': shadow})

    def setShape(self, shape):
        self.setOptions({'shape': shape})

    def setTitle(self, title):
        self.setOptions({'title': title})

    def setVisible(self, visible):
        self.setOptions({'visible': visible})

    def setZIndex(self, zIndex):
        self.setOptions({'zIndex': zIndex})


class MarkerImage(MapClass):
    """An image to be used as the icon or shadow for a Marker.

    Equivalent to google.maps.MarkerImage. When parsed by
    JSONEncoder and subsequently by our custom jQuery plugin,
    it will be converted to an actual google.maps.MarkerImage
    instance.

    """
    def __init__(self, url, size=None, origin=None, anchor=None,
                 scaledSize=None):
        super(MarkerImage, self).__init__(cls='MarkerImage')
        self['arg'] = Args(['url', 'size', 'origin', 'anchor', 'scaledSize'],
                           [url])
        if size:
            self['arg'].setdefault('size', size)
        if origin:
            self['arg'].setdefault('origin', origin)
        if anchor:
            self['arg'].setdefault('anchor', anchor)
        if scaledSize:
            self['arg'].setdefault('scaledSize', scaledSize)

    def __unicode__(self):
        return self['arg'].get('url')


class Geocoder(object):
    """A service for converting between an address and a LatLng.

    This is equivalent to using google.maps.Geocoder except that
    it makes use of the Web Service. You should always use the
    javascript API version in preference to this one as query
    limits are per IP. The javascript API uses the client's IP
    and thus is much less likely to hit any limits.

    """
    # Handle blocking and sleeping at class level.
    _block = False
    _sleep = 0

    def geocode(self, request, callback=None):
        """Geocode a request.

        Unlike the javascript API, this method is blocking. So, even
        though a callback function is supported, the method will also
        return the results and status directly.

        """
        # Handle any unicode in the request.
        if 'address' in request:
            request['address'] = smart_str(request['address'],
                                           strings_only=True).lower()
        # Add the sensor parameter if needed.
        if 'sensor' in request:
            if request['sensor'] != 'false':
                request['sensor'] = 'true' if request['sensor'] else 'false'
        else:
            request['sensor'] = 'false'
        cache_key = urlencode(request)
        url = '%s/json?%s' % (GEOCODE_URL, cache_key)
        # Try up to 30 times if over query limit.
        for _ in xrange(30):
            # Check if result is already cached.
            data = cache.get(cache_key)
            nocache = data is None
            if nocache:
                # Wait a bit so that we don't make requests too fast.
                time.sleep(self._sleep)
                data = urllib.urlopen(url).read()
            response = loads(data)
            status = response['status']

            if status == 'OVER_QUERY_LIMIT':
                # Over limit, increase delay a bit.
                if self._block:
                    break
                self._sleep += .1
            else:
                # Save results to cache.
                if nocache:
                    cache.set(cache_key, data)
                if status == 'OK':
                    # Successful query, clear block if there is one.
                    if self._block:
                        self._block = False
                        self._sleep = 0
                    results = _parseGeocoderResult(response['results'])
                    if callback:
                        callback(results, status)
                    return results, status
                else:
                    return None, status
        self._block = True
        raise SystemError('Geocoding has failed too many times. '
                          'You might have exceeded your daily limit.')


def _parseGeocoderResult(result):
    """ Parse Geocoder Results.

    Traverses the results converting any latitude-longitude pairs
    into instances of LatLng and any SouthWest-NorthEast pairs
    into instances of LatLngBounds.

    """
    # Check for LatLng objects and convert.
    if (isinstance(result, dict) and 'lat' in result and 'lng' in result):
        result = LatLng(result['lat'], result['lng'])
    # Continue traversing.
    elif isinstance(result, dict):
        for item in result:
            result[item] = _parseGeocoderResult(result[item])
        # Check for LatLngBounds objects and convert.
        if ('southwest' in result and 'northeast' in result):
            result = LatLngBounds(result['southwest'], result['northeast'])
    elif isinstance(result, (list, tuple)):
        for index in xrange(len(result)):
            result[index] = _parseGeocoderResult(result[index])
    return result


class LatLng(MapClass):
    """A point in geographical coordinates, latitude and longitude.

    Equivalent to google.maps.LatLng. When parsed by JSONEncoder
    and subsequently by our custom jQuery plugin, it will be
    converted to an actual google.maps.LatLng instance.

    """
    def __init__(self, lat, lng, noWrap=None):
        super(LatLng, self).__init__(cls='LatLng')
        self['arg'] = Args(['lat', 'lng', 'noWrap'], [Degree(lat), Degree(lng)])
        if noWrap is not None:
            self['arg'].setdefault('noWrap', noWrap)

    def __unicode__(self):
        return self.toUrlValue()

    def equals(self, other):
        return (self.lat() == other.lat() and self.lng() == other.lng())

    def lat(self):
        return self['arg'].get('lat')

    def lng(self):
        return self['arg'].get('lng')

    def toString(self):
        return '(%s, %s)' % (self.lat(), self.lng())

    def toUrlValue(self, precision=6):
        return '%s,%s' % (Degree(self.lat(), precision),
                          Degree(self.lng(), precision))


class LatLngBounds(MapClass):
    """A rectangle in geographical coordinates.

    Equivalent to google.maps.LatLngBounds. When parsed by
    JSONEncoder and subsequently by our custom jQuery plugin,
    it will be converted to an actual google.maps.LatLngBounds
    instance.

    """
    def __init__(self, sw=None, ne=None):
        super(LatLngBounds, self).__init__(cls='LatLngBounds')
        self['arg'] = Args(['sw', 'ne'])
        if sw:
            self['arg'].setdefault('sw', sw)
        if ne:
            self['arg'].setdefault('ne', ne)

    def __unicode__(self):
        return self.toUrlValue()

    def contains(self, point):
        raise NotImplementedError

    def equals(self, other):
        # Check if our corners are equal.
        return (self.getSouthWest().equals(other.getSouthWest()) and
                self.getNorthEast().equals(other.getNorthEast()))

    def extend(self, point):
        raise NotImplementedError

    def getCenter(self):
        raise NotImplementedError

    def getNorthEast(self):
        return self['arg'].get('ne')

    def getSouthWest(self):
        return self['arg'].get('sw')

    def intersects(self, other):
        raise NotImplementedError

    def isEmpty(self):
        return ((not self.getSouthWest()) or
                (self.getNorthEast() and
                 self.getSouthWest().lat() >
                 self.getNorthEast().lat()))

    def toSpan(self):
        raise NotImplementedError

    def toString(self):
        return '(%s, %s)' % (self.getSouthWest().toString(),
                             self.getNorthEast().toString())

    def toUrlValue(self, precision=6):
        return '%s,%s' % (self.getSouthWest().toUrlValue(precision),
                          self.getNorthEast().toUrlValue(precision))

    def union(self, other):
        raise NotImplementedError


class Point(MapClass):
    """A point on a two-dimensional plane.

    Equivalent to google.maps.Point. When parsed by JSONEncoder
    and subsequently by our custom jQuery plugin, it will be
    converted to an actual google.maps.Point instance.

    """
    def __init__(self, x, y):
        super(Point, self).__init__(cls='Point')
        self['arg'] = Args(['x', 'y'], [x, y])

    def __unicode__(self):
        return '%s,%s' % (self['arg'].get('x', 0),
                          self['arg'].get('y', 0))

    def _getX(self):
        return self['arg'][0]

    def _getY(self):
        return self['arg'][1]

    def _setX(self, x):
        self['arg'][0] = x

    def _setY(self, y):
        self['arg'][1] = y

    def equals(self, other):
        return self.x == other.x and self.y == other.y

    def toString(self):
        return '(%s, %s)' % (self.x, self.y)

    x = property(_getX, _setX)

    y = property(_getY, _setY)


class Size(MapClass):
    """A two-dimensonal size.

    Equivalent to google.maps.Size. When parsed by JSONEncoder
    and subsequently by our custom jQuery plugin, it will be
    converted to an actual google.maps.Size instance.

    """
    def __init__(self, width, height, widthUnit=None, heightUnit=None):
        super(Size, self).__init__(cls='Size')
        self['arg'] = Args(['width', 'height', 'widthUnit', 'heightUnit'],
                           [int(width), int(height)])
        if widthUnit:
            self['arg'].setdefault('widthUnit', widthUnit)
        if heightUnit:
            self['arg'].setdefault('heightUnit', heightUnit)

    def __unicode__(self):
        return '%sx%s' % (self['arg'].get('width', 0),
                          self['arg'].get('height', 0))

    def _getHeight(self):
        return self['arg'][1]

    def _getWidth(self):
        return self['arg'][0]

    def _setHeight(self, height):
        self['arg'][1] = height

    def _setWidth(self, width):
        self['arg'][0] = width

    def equals(self, other):
        return self.width == other.width and self.height == other.height

    def toString(self):
        return '(%s, %s)' % (self.width, self.height)

    height = property(_getHeight, _setHeight)

    width = property(_getWidth, _setWidth)


class Degree(float):
    """A custom float class for degrees.

    For holding degrees of a circle (latitude and longitude).
    When converted to a string or parsed by JSONEncoder, it
    will output with, at most, the specified precision.

    """
    def __new__(cls, value, precision=6):
        return float.__new__(cls, value)

    def __init__(self, value, precision=6):
        super(Degree, self).__init__()
        self.precision = precision

    def __repr__(self):
        return (('%%0.%df' % self.precision) % self).rstrip('0').rstrip('.')

    def __unicode__(self):
        return self.__repr__()

    def __str__(self):
        return self.__repr__()


class Args(list):
    """A custom list that implements setdefault and get by name."""
    def __init__(self, names, values=None):
        super(Args, self).__init__(values or [])
        self.names = names

    def get(self, name, default=None):
        i = self.names.index(name)
        return self[i] if len(self) > i else default

    def setdefault(self, name, default=None):
        i = self.names.index(name)
        if len(self) <= i or self[i] is None:
            # Fill gaps with None.
            self.extend(None for _ in xrange(len(self), i))
            self.append(default)
        return self[i]
