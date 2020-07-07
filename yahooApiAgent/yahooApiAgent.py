import os
import requests
import datetime
import logging
import json
from homeUtil import handleEnvironment

LOG_LEVEL = logging.DEBUG


class yahooApiAgent:

    def __init__(self):

        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

        self.URL_YOLP_WEATHER = 'https://map.yahooapis.jp/weather/V1/place'
        self.YAHOO_API_KEY = os.environ['YAHOO_API_KEY']
        self.LATITUDE = os.environ['GEO_LATITUDE']
        self.LONGITUDE = os.environ['GEO_LONGITUDE']

    def getRainLevel(self, time=0):

        now = datetime.datetime.now()
        print(now)

        appid = '?appid=' + self.YAHOO_API_KEY
        coodinate = '&coordinates=' + self.LONGITUDE + ',' + self.LATITUDE
        output = '&output=' + 'json'
        date = '&date=' + now.strftime('%Y%m%d%H%M')
        interval = '&interval=5'
        past = '&past=1'

        req = self.URL_YOLP_WEATHER + appid + coodinate + output + date + interval + past

        try:
            res = requests.get(url=req)
            self.log.info(f'get url:{req} succeed.')

            weather_list = json.loads(res.text)['Feature'][0]['Property']['WeatherList']['Weather']
            print(weather_list)
            print(json.loads(res.text)['Feature'][0]['Name'])

        except Exception as e:
            self.log.error(e)
            weather_list = None

        return weather_list
