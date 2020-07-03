import os
import requests
import datetime


class yahooApiAgent():

    def __init__(self):

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

        print(date)
        # req = self.URL_YOLP_WEATHER + appid + coodinate + output + date + interval
        req = self.URL_YOLP_WEATHER + appid + coodinate + output + date + interval

        res = requests.get(url=req)
        print(res.text)

        """res json
        {
            'rainfall':{
                'current':'0.00',
                'forcast':{
                    5:
                }
            }
            'device':'Yahoo Weather API'
        }
        """


if __name__ == "__main__":

    ya = yahooApiAgent()
    ya.getRainLevel()

    pass
