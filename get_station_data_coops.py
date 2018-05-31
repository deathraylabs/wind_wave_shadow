"""Script to download National Data Buoy Center data from their SOS server.

Details regarding how to access the NDBC data can be found at their SOS website:
`<https://sdf.ndbc.noaa.gov/sos/>_`

note
----

- wave directions are reported in the direction they're headed *to*,
not *from* as they are at other sites.
"""

import requests
import json
from dateutil import parser
from dateutil import tz
import pprint as p


def utc_to_local_time(utc_iso_string):
    """Convert UTC timestamp to local timestamp (ISO 8601)"""
    utc_time = parser.parse(utc_iso_string)
    local_zone = tz.tzlocal()

    return utc_time.astimezone(local_zone)


def get_station_data(station_id, data_product, fieldnames=None):
    """Grab data from NDBC SOS site

    Parameter
    ---------
    station_id : str or int
        This is a 7-digit station identifier.
    data_product : str
        One of the _observedproperty_ values available from the server.
    fieldvalues : list
        List of field value strings you'd like returned from the NDBC server.

    """
    # station ID values must be 7-digit number
    station_id = str(station_id)
    # offering = 'urn:ioos:station:wmo:' + station_id

    # this is the SOS server website we'll append our request to
    url_prefix = 'https://tidesandcurrents.noaa.gov/api/datagetter?'

    # dict containing the specifics of our request. See IOOS site for details.
    payload = {
        'date':         'latest',
        'station':       station_id,
        'product':      'wind',
        'units':        'english',
        'time_zone':    'lst_ldt',        # local standard and DST
        'format':       'json',           # csv, json, xml available
        'application':  'Philip Smith'    # name of organization
    }

    # reformat the payload using typical HTTP POST syntax
    # this step is necessary if there are colons in the request that
    # cannot be escaped out or the request will be rejected as invalid
    payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())

    # `requests.post()` doesn't work for some reason but get does
    r = requests.get(url_prefix, params=payload_str)

    # weather station data file in format csv module can handle
    weather_file = r.text

    # convert csv data to dictionary
    # weather_data = csv.DictReader(weather_file, delimiter=',')

    # dict representation of the station weather data provided
    weather_data = json.loads(weather_file)

    return weather_data


# test code to see how the function operates

# field names for values I'd like returned
# waves_field_names = [
#                      'date_time',
#                      'sea_surface_wave_significant_height (m)',
#                      'sea_surface_wave_peak_period (s)',
#                      'sea_surface_wave_to_direction (degree)',
#                     ]
#
# winds_field_names = [
#                      'date_time',
#                      'depth (m)',
#                      'wind_from_direction (degree)',
#                      'wind_speed (m/s)',
#                      'wind_speed_of_gust (m/s)',
#                     ]

# # sos_data = get_station_data(42019, 'waves', field_names)
# sos_data = get_station_data(42019, 'waves', waves_field_names)
# print("waves data:\n")
# p.pprint(sos_data)

# raw data dictionary
coops_data_raw = get_station_data('8772447', 'wind')
# the actual wind data
wind_data_dict = coops_data_raw['data'][0]

obs_time = wind_data_dict['t']
wind_speed = wind_data_dict['s']
wind_dir = wind_data_dict['d']

another_try = coops_data_raw['data'][0]['s']

print("wind data:\n"
      '\n'
      'observation time: {}\n'
      'wind direction:   {}°\n'
      'wind speed:       {} mph\n'.format(obs_time, wind_dir, wind_speed)
      )
