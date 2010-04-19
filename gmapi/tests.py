"""
>>> from gmapi import maps

# Test MapDiv creation.
>>> d = maps.MapDiv(510, 510)
>>> d
{'div': {'width': 510, 'height': 510}}

# Test Map creation.
>>> m = maps.Map(d)
>>> m
{'arg': [{'div': {'width': 510, 'height': 510}}], 'cls': 'maps.Map'}

# Make sure getDiv returns the original Node.
>>> m.getDiv()
{'div': {'width': 510, 'height': 510}}

# Test setting and getting the map center.
>>> m.setCenter(maps.LatLng(38, -97))
>>> m.getCenter()
{'arg': [38, -97], 'cls': 'maps.LatLng'}

# Test setting the map type.
>>> m.setMapTypeId(maps.MapTypeId.ROADMAP)
>>> m.getMapTypeId()
{'val': 'maps.MapTypeId.ROADMAP'}

# Test setting and getting the zoom.
>>> m.setZoom(3)
>>> m.getZoom()
3

# Test LatLngBounds creation.
>>> b = maps.LatLngBounds(maps.LatLng(18, -119), maps.LatLng(53, -74))
>>> b
{'arg': [{'arg': [18, -119], 'cls': 'maps.LatLng'}, {'arg': [53, -74], 'cls': 'maps.LatLng'}], 'cls': 'maps.LatLngBounds'}

# Test setting multiple options at once.
>>> m.setOptions({'center': maps.LatLng(0, 0), 'zoom': 4, 'mapTypeId': maps.MapTypeId.SATELLITE})
>>> m
{'arg': [{'div': {'width': 510, 'height': 510}}, {'mapTypeId': {'val': 'maps.MapTypeId.SATELLITE'}, 'center': {'arg': [0, 0], 'cls': 'maps.LatLng'}, 'zoom': 4}], 'cls': 'maps.Map'}

# Test creating a marker.
>>> k = maps.Marker()
>>> k.setPosition(maps.LatLng(38, -97))
>>> k.setMap(m)
>>> k
{'arg': [{'position': {'arg': [38, -97], 'cls': 'maps.LatLng'}}], 'cls': 'maps.Marker'}

# Make sure the marker was added to the map.
>>> m
{'arg': [{'div': {'width': 510, 'height': 510}}, {'mapTypeId': {'val': 'maps.MapTypeId.SATELLITE'}, 'center': {'arg': [0, 0], 'cls': 'maps.LatLng'}, 'zoom': 4}], 'mkr': [{'arg': [{'position': {'arg': [38, -97], 'cls': 'maps.LatLng'}}], 'cls': 'maps.Marker'}], 'cls': 'maps.Map'}


"""
