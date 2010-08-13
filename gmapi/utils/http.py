import urllib


def urlencode(query, doseq=0):
    """Custom urlencode that leaves static map delimiters alone."""
    url = urllib.urlencode(query, doseq)
    def parse(p):
        # Process each key and value.
        p = map(lambda s:
                # Unquote then quote each item.
                urllib.quote_plus(urllib.unquote_plus(s), '|,:'),
                p.split('='))
        return '='.join(p)
    # Process each key-value pair.
    return '&'.join(map(parse, url.split('&')))
