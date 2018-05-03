"""Script to download National Data Buoy Center data from their SOS server.

Details regarding how to access the NDBC data can be found at their SOS website:
`<https://sdf.ndbc.noaa.gov/sos/>_`

note
----

- wave directions are reported in the direction they're headed *to*,
not *from* as they are at other sites.
"""

import requests
import csv
from io import StringIO
from dateutil import parser
from dateutil import tz

def utc_to_local_time(utc_iso_string):
    """Convert UTC timestamp to local timestamp (ISO 8601)"""
    utc_time = parser.parse(utc_iso_string)
    local_zone = tz.tzlocal()

    return utc_time.astimezone(local_zone)


def get_sos_data(station_id, observed_property):
    # station ID values must be upper case strings if not numeric
    station_id = str(station_id).upper()
    offering = 'urn:ioos:station:wmo:' + station_id

    # this is the SOS server website we'll append our request to
    url_prefix = 'https://sdf.ndbc.noaa.gov/sos/server.php'

    # dict containing the specifics of our request. See IOOS site for details.
    payload = {'request': 'GetObservation',
               'service': 'SOS',
               'version': '1.0.0',
               'offering': offering,
               'observedproperty': observed_property,
               'responseformat': 'text/csv',
               'eventtime': 'latest'}

    # reformat the payload using typical HTTP POST syntax
    # this step is necessary because there are colons in the request that
    # cannot be escaped out or the request will be rejected as invalid
    payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())

    # `requests.post()` doesn't work for some reason but get does
    r = requests.get(url_prefix, params=payload_str)

    # weather station data file in format csv module can handle
    weather_file = StringIO(r.text)

    # convert text data to dictionary
    weather_data = csv.DictReader(weather_file, delimiter=',')
    weather_fieldnames = weather_data.fieldnames

    for line in weather_data:
        for fieldname in weather_fieldnames:
            fieldvalue = line[fieldname]
            print(fieldname + ": " + fieldvalue)

    # print(r.text)

sos_data = get_sos_data(42019, 'waves')