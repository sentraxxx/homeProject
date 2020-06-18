import json
import requests
import os


class natureRemoAgent():
    """[summary]
    nature remo apiのAgent.
    5分間に30回の制限あり。
    制限の残りはlimit-remainで確認。
    """

    def __init__(self):

        self.NATURE_AUTH = os.environ["NATURE_AUTH"]
        self.NATURE_ID = os.environ["NATURE_ID"]
        self.NATURE_URL = "https://api.nature.global/"

    def getTemp(self) -> dict:
        """[summary]
        nature remo apiのdevicesをcall.
        使える値は室温くらい。

        Returns:
            dict: temp: 室温
            limit-remain: 残り回数 
        """

        endpoint = self.NATURE_URL + "1/devices"
        authorization_header = 'Bearer ' + self.NATURE_AUTH

        headers = {
            'accept': 'application/json',
            'Authorization': authorization_header,
        }

        print("endpoint:", endpoint)
        print("headers:", headers)

        res = requests.get(endpoint, headers=headers)

        resj = json.loads(res.text)

        temp = resj[0]["newest_events"]["te"]["val"]
        limit_remain = res.headers["X-Rate-Limit-Remaining"]

        return {"temp": temp, "limit-remain": limit_remain}


if __name__ == "__main__":

    agent = natureRemoAgent()
    res = agent.getTemp()
    print("temp: ", res["temp"])

    pass

