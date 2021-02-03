import os
import requests
import logging
import json
from homeUtil import handleEnvironment

LOG_LEVEL = logging.DEBUG


class accuWeatherAgent:

    def __init__(self):

        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

        self.API_KEY = os.environ['ACCU_WEATHER_API_KEY']

        self.BASE_URL = 'https://dataservice.accuweather.com'
        self.GEO_LAT = os.environ['GEO_LATITUDE']
        self.GEO_LON = os.environ['GEO_LONGITUDE']

    def getLocation(self):

        api = '/locations/v1/cities/geoposition/search?'
        lat = self.GEO_LAT
        lon = self.GEO_LON
        apikey = self.API_KEY

        url = self.BASE_URL + api + f'apikey={apikey}&q={lat},{lon}'
        self.log.debug(f'url={url}')
        res = requests.get(url)

        self.log.debug(res.text)

        resj = json.loads(res.text)
        locationId = resj['Key']

        return locationId

    def getWether(self, location='1510153'):

        api = '/currentconditions/v1/'
        apikey = self.API_KEY

        req = self.BASE_URL + api + location + f'?apikey={apikey}'
        self.log.debug(f'request={req}')

        res = requests.get(req)
        self.log.debug(res.text)
