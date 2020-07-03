import os
import requests
import logging
import datetime
import json
from homeUtil import handleEnvironment


LOG_LEVEL = logging.DEBUG


class openWeatherAgent:

    def __init__(self):

        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

        self.API_KEY = os.environ['OPEN_WEATHER_API_KEY']

        self.GEO_LAT = os.environ['GEO_LATITUDE']
        self.GEO_LON = os.environ['GEO_LONGITUDE']

        self.BASE_URL_ONE_CALL = 'https://api.openweathermap.org/data/2.5/onecall?'
        self.BASE_URL_CURRENT_WEATHER = 'https://api.openweathermap.org/data/2.5/weather?'

    def getCurrentOneCall(self) -> json:

        lat = self.GEO_LAT
        lon = self.GEO_LON
        appid = self.API_KEY

        req = self.BASE_URL_ONE_CALL + f'lat={lat}&lon={lon}&units=metric&lang=ja&appid={appid}'
        res = requests.get(req)
        self.log.debug(res.text)

        return res.text

    def getCurrentWeatherByGeo(self) -> json:

        lat = self.GEO_LAT
        lon = self.GEO_LON
        appid = self.API_KEY

        req = self.BASE_URL_CURRENT_WEATHER + f'lat={lat}&lon={lon}&units=metric&lang=ja&appid={appid}'
        res = requests.get(req)
        self.log.debug(res.text)

        return res.text

    def utcToJst(self, dt: int) -> datetime:

        # offset = 32400
        jst = datetime.datetime.fromtimestamp(dt)

        return jst
