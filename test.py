from homeLogger import environmentLogger
from yahooApiAgent import yahooApiAgent
from openWeatherAgent import openWeatherAgent
from accuWeatherAgent import accuWeatherAgent
from homeDb import mariaDbAgent, dbTester
from natureRemo import natureRemoAgent
import requests
import json

# mariadb getDataテスト.
agent = mariaDbAgent()
res = agent.getData(cols=['type', 'subtype', 'datetime'], w_column=['type'], w_value=['record'], order='datetime', by='desc')
print(res)
print(len(res))

# mariadb setNotifyAlarmテスト.
"""agent = mariaDbAgent()
agent.setNotifyAlarm('test')"""


# mariadb setEnvテスト.
"""agent = mariaDbAgent()
agent.setEnv(param=mariaDbAgent.ENV_MAKE_NOTIFY, value=mariaDbAgent.ENV_ON)"""


# makeNotifyテスト.
"""URL = 'http://localhost:5000/makeNotify'
res = requests.get('http://localhost:5000/')
print("code:", res, " body:", res.text)
data = {'text': 'a'}
res = requests.post(URL, json=data)
print(res)"""

# yahooAPIテスト.
"""agent = yahooApiAgent()
agent.getRainLevel()"""

# environment Loggerテスト.
"""agent = environmentLogger()
el.recordWeather()
el.recordRaspberryPiTemp()
agent.recordHomeTemp()"""

# OpenWeather APIテスト
"""openweather = openWeatherAgent()
openweather.getCurrentOneCall()
# openweather.getCurrentWeatherByGeo()"""

# accuWeatherのテスト
"""acc = accuWeatherAgent()
acc.getWether()"""

# DB テストモード
"""agent = dbTester()
# print(agent.testSelectCount(['type', 'subtype'], ['condition', 'current_']))
agent.testSelectCount(['type', 'subtype'], ['record', 'temp'])"""
