import requests
import logging
import sys
import os

sys.path.append('/home/pi/share/dev/homeProject/')

LOG_LEVEL = logging.DEBUG


class googleHome:

    def __init__(self):
        pass

    def sendMessage(self, message: str):
        """google homeにしゃべらせる.

        Args:
            message (str): しゃべらせるメッセージ

        Returns:
            status_code (int): HTTP response code.
        """
        URL = 'http://localhost:5000/makeNotify'
        data = {'text': message, 'id': 1, 'em': 1, 'emlv': 1, 'pitch': 90, 'speed': 100, 'volume': 50}
        res = requests.post(URL, json=data)

        return res.status_code


class ifttt:

    def __init__(self):

        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

        self.BASE_URL = 'https://maker.ifttt.com/trigger/'
        self.BASE2_URL = '/with/key/'
        self.KEY = os.environ['IFTTT_WEBHOOK_KEY']

        self.ANDROID_NOTIFY = 'android_notify'

    def post(self, event: str, value1=None, value2=None, value3=None):

        values_j = {'value1': value1, 'value2': value2, 'value3': value3}
        url = self.BASE_URL + event + self.BASE2_URL + self.KEY

        try:
            result = requests.post(url, json=values_j)

        except Exception as e:
            self.log.error(e)
            self.log.error('send message (android_notify) failed.')

        return result

    def sendMessage(self, message: str):
        """IFTTTのwebhook経由でAndroid端末にIFTTT通知を送る.

        Args:
            message (str): 送信するメッセージ.

        Returns:
            result : requests.postのレスポンス.
        """

        result = self.post(self.ANDROID_NOTIFY, value1=message)

        return result
