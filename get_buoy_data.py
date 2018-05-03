""" Grab wind/swell data from buoy site """

import requests
import csv
from io import StringIO
from datetime import datetime
from dateutil import tz


def current_buoy_data(stationid='42019'):
    # standard meteorological data provided by stations
    # plus additional entry for local measurement time
    std_met_data = {'wind direction': 'WDIR',
                    'wind speed': 'WSPD',
                    'gust speed': 'GST',
                    'significant wave height': 'WVHT',
                    'dominant wave period': 'DPD',
                    'dominant wave direction': 'MWD',
                    'measurement time': 'TIME'
                    }

    # column_names = ('#YY', 'MM', 'DD', 'hh', 'mm', 'WDIR', 'WSPD', 'GST', 'WVHT',
    #                 'DPD', 'APD', 'MWD', 'PRES', 'ATMP', 'WTMP', 'DEWP', 'VIS',
    #                 'PTDY', 'TIDE')

    # base url used to get to "realtime" station data
    url_base = 'http://www.ndbc.noaa.gov/data/realtime2/'

    # station ID that you want to grab data from (if letters must be all caps)
    station_id = stationid.upper()

    # type of data you're interested in (create dict later if you want)
    data_type = '.txt'    # this is standard meteorological data

    complete_url = url_base + station_id + data_type
    print(complete_url)

    # get the data with requests
    res = requests.get(complete_url)

    print(res.status_code == requests.codes.ok)

    # weather station data file in format csv module can handle
    weather_file = StringIO(res.text)

    # convert text data to dictionary
    weather_data = csv.DictReader(weather_file, delimiter=' ',
                                  skipinitialspace=True)

    # newest data is on the third row
    line_number = 0
    newest_data = dict()
    for line in weather_data:
        if line_number == 2:
            break
        else:
            newest_data = line
        # incrementer
        line_number += 1

    print(newest_data)

    print(newest_data['ATMP'])

    # get the timestamp from the most recent measurement
    most_recent_utc = newest_data['#YY'] + '-' \
                    + newest_data['MM']  + '-' \
                    + newest_data['DD']  + ' ' \
                    + newest_data['hh']  + ':' \
                    + newest_data['mm']

    print('most recent time utc ' + most_recent_utc)

    # autodetect timezones
    utc_zone = tz.tzutc()
    local_zone = tz.tzlocal()

    # convert parsed text to datetime object
    utc = datetime.strptime(most_recent_utc, '%Y-%m-%d %H:%M')

    # tell datetime object what timezone the most recent measurement is in
    utc = utc.replace(tzinfo=utc_zone)

    # now convert this time to local time
    most_recent_time = utc.astimezone(local_zone)
    newest_data['TIME'] = most_recent_time

    print('most recent measurement at ' + str(most_recent_time))

    print('The significant wave height is:')
    print(newest_data[std_met_data['significant wave height']])

    return newest_data[std_met_data['dominant wave direction']], newest_data[
        std_met_data['wind direction']], newest_data[
        std_met_data['dominant wave period']]
