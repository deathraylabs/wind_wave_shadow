"""Script to download National Data Buoy Center data from their SOS server.

Details regarding how to access the NDBC data can be found at their SOS website:
`<https://sdf.ndbc.noaa.gov/sos/>_`
"""

import requests

# this is the SOS server website we'll append our request to
url_prefix = 'https://sdf.ndbc.noaa.gov/sos/server.php'

# dict containing the specifics of our request. See IOOS site for details.
payload = {'request': 'GetObservation',
           'service': 'SOS',
           'version': '1.0.0',
           'offering': 'urn:ioos:station:wmo:41012',
           'observedproperty': 'air_pressure_at_sea_level',
           'responseformat': 'text/csv',
           'eventtime': 'latest'}

# reformat the payload using typical HTTP POST syntax
# this step is necessary because there are colons in the request that
# cannot be escaped out or the request will be rejected as invalid
payload_str =  "&".join("%s=%s" % (k,v) for k,v in payload.items())

# `requests.post()` doesn't work for some reason but get does
r = requests.get(url_prefix, params=payload_str)

print(r.text)