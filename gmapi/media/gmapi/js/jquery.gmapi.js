jQuery(function($){

    // Return new instance of a class using an array of parameters.
    function instance(constructor, args){
        function F(){
            return constructor.apply(this, args);
        }
        F.prototype = constructor.prototype;
        return new F();
    }

    // Return a property value by name (descendant of google.maps by default).
    function property(path, context){
        context = context || window.google.maps;
        path = path.split('.');
        if (path.length > 1) {
            return property(path.slice(1).join('.'), context[path[0]]);
        }
        else {
            return context[path[0]];
        }
    }

    // Traverses any plain object or array. When an object with valid keys
    // is encountered, it's converted to the indicated type.
    // This allows us to create instances of classes and reference built-in
    // constants within a simple JSON style object.
    //
    // Valid keys:
    //   cls    The name of a class constructor (descendant of google only).
    //     arg  Array of positional parameters for class constructor.
    //   div    Placeholder for DOM node. Contains styles to be applied.
    //   val    The name of a property or constant (descendant of google only).
    function parse(obj, div){
        // Handle a div.
        if (obj === 'div') {
            // Apply styles and return first element.
            return div;
        }
        if ($.isPlainObject(obj) || $.isArray(obj)) {
            // Handle a new class instance.
            if (obj.cls) {
                // Handle initialization parameters.
                var args = [];
                if (obj.arg) {
                    for (var a in obj.arg) {
                        args.push(parse(obj.arg[a], div));
                    }
                }
                return instance(property(obj.cls), args);
            }
            // Handle a property or constant.
            if (obj.val) {
                return property(obj.val);
            }
            // Handle any other iterable.
            for (var k in obj) {
                obj[k] = parse(obj[k], div);
            }
        }
        return obj;
    }

    // Clear all markers and remove them.
    $.fn.removeMarkers = function(){
        return this.each(function(){
            var div = $(this);
            // Get any existing markers.
            var markers = div.data('markers');
            for (var m in markers) {
                // Clear it from the map.
                markers[m].setMap(null);
            }
            // Remove from div data.
            div.removeData('markers');
        });
    };

    // Add and render an array of markers.
    $.fn.addMarkers = function(obj){
        return this.each(function(){
            if (obj) {
                var div = $(this);
                // Get a map reference.
                var map = div.data('map');
                // Get any existing markers.
                var markers = div.data('markers') || [];
                for (var m in obj) {
                    // Parse the marker.
                    var marker = parse(obj[m], this);
                    // Render it to the map.
                    marker.setMap(map);
                    // Add the marker to our array.
                    markers.push(marker);
                }
                // Save the marker array to div data.
                div.data('markers', markers);
            }
            // Only add markers to first element.
            return false;
        });
    };

    $.fn.fitMarkers = function(){
        return this.each(function(){
            var div = $(this);
            // Get a map reference.
            var map = div.data('map');
            // Get any existing markers.
            var markers = div.data('markers');
            if (map && markers) {
                // Create a new bounds object.
                var bounds = new google.maps.LatLngBounds();
                for (var m in markers) {
                    // Add all the markers to the bounds.
                    bounds.extend(markers[m].getPosition());
                }
                // Fit the map to the bounds.
                map.fitBounds(bounds);
            }
        });
    };

    // Create a new map.
    $.fn.newMap = function(obj){
        return this.each(function(){
            var div = $(this);
            // Get rid of any existing markers.
            div.removeMarkers().removeData('map');
            // Parse the map.
            var map = parse(obj, div.children('div')[0]);
            // Save the map to div data.
            div.data('map', map);
            // Handle markers.
            if (obj.mkr) {
                div.addMarkers(obj.mkr);
                // Auto-size map if no center or zoom given.
                if (!(map.getCenter() && map.getZoom() >= 0)) {
                    div.fitMarkers();
                }
            }
            // Send a newmap trigger.
            div.trigger('newmap');
            // Only add map to first element.
            return false;
        });
    };

    // Startup: Find any maps and initialize them.
    $('div.gmap:visible').each(function(){
        var div = $(this);
        var mapdiv = div.children('div');
        var data = mapdiv.attr('class').match(/{.*}/)[0];
        if (data) {
            mapdiv.removeClass();
            div.newMap($.parseJSON(data));
            var mapimg = div.children('img');
            var t = window.setTimeout(function(){
                mapimg.css('z-index', -1);
            }, 2000);
            google.maps.event.addListenerOnce(div.data('map'), 'tilesloaded', function(){
                window.clearTimeout(t);
                mapimg.css('z-index', -1);
            });
        }
    });

});
