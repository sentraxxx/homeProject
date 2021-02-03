import json
import requests
import os
import logging
import sys

sys.path.append('/home/pi/share/dev/homeProject/src')

from homeUtil import handleEnvironment

LOG_LEVEL = logging.INFO


class natureRemoAgent:
    """[summary]
    nature remo apiのAgent.
    5分間に30回の制限あり。
    制限の残りはlimit-remainで確認。
    """

    def __init__(self):

        self.NATURE_AUTH = os.environ["NATURE_AUTH"]
        self.NATURE_ID = os.environ["NATURE_ID"]
        self.NATURE_URL = "https://api.nature.global/"

        # Log Set.
        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

    def getTemp(self) -> dict:
        """nature remo apiのdevicesをcall.使える値は室温くらい。

        Returns:
            dict: temp=室温、limit-remain: 残り回数
        """

        endpoint = self.NATURE_URL + "1/devices"
        authorization_header = 'Bearer ' + self.NATURE_AUTH

        headers = {
            'accept': 'application/json',
            'Authorization': authorization_header,
        }

        self.log.debug("endpoint:" + str(endpoint))
        self.log.debug("headers:" + str(headers))

        res = requests.get(endpoint, headers=headers)

        resj = json.loads(res.text)

        temp = resj[0]["newest_events"]["te"]["val"]
        limit_remain = res.headers["X-Rate-Limit-Remaining"]

        self.log.debug("temp= " + str(temp) + ", limit_remain= " + str(limit_remain))

        return {"temp": temp, "limit-remain": limit_remain}


if __name__ == "__main__":

    agent = natureRemoAgent()
    res = agent.getTemp()
    print("temp: ", res["temp"])

    pass
