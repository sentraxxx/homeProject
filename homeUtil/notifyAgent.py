import requests
import logging
import sys

from homeDb import mariaDbAgent

sys.path.append('/home/pi/share/dev/homeProject/')


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


