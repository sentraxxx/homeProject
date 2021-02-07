from homeLogger import environmentLogger
from yahooApiAgent import yahooApiAgent
from openWeatherAgent import openWeatherAgent
from accuWeatherAgent import accuWeatherAgent
from homeDb import mariaDbAgent, dbTester
from natureRemo import natureRemoAgent
from homeUtil import googleHome, handleEnvironment, ifttt
from homeGate.gateFunctions import gateFunc
import datetime
import requests
import json


# seacrhOsewaRecordテスト
# func = gateFunc()
# res = func.searchOsewaRecord({'when': '前回', 'who': 'ジョルノ', 'category': 'トイレシート交換'})
# print(type(res))
# print(func.searchOsewaRecord({'when': '今日', 'who': 'ジョルノ', 'category': 'トイレシート交換'}))
# print(func.searchOsewaRecord({'when': '昨日', 'who': 'ジョルノ', 'category': 'トイレシート交換'}))
# print(func.searchOsewaRecord({'when': '今月', 'who': 'ジョルノ', 'category': 'トイレシート交換'}))
# print(func.searchOsewaRecord({'when': '先月', 'who': 'ジョルノ', 'category': 'トイレシート交換'}))
# print('-------')
# print(func.searchOsewaRecord({'when': '前回', 'who': 'ジョルノ', 'category': 'うんち'}))
# print(func.searchOsewaRecord({'when': '今日', 'who': 'ジョルノ', 'category': 'うんち'}))
# print(func.searchOsewaRecord({'when': '昨日', 'who': 'ジョルノ', 'category': 'うんち'}))
# print(func.searchOsewaRecord({'when': '今月', 'who': 'ジョルノ', 'category': 'うんち'}))
# print(func.searchOsewaRecord({'when': '先月', 'who': 'ジョルノ', 'category': 'うんち'}))

# DBのconnection調査
# agent = mariaDbAgent()
# agent.setNotifyAlarm("日本語")

# IFTTTに通知
# agent = ifttt()
# agent.sendMessage('test message')

# google homeにしゃべらせる
"""google = googleHome()
db = mariaDbAgent()
db.setVoiceTextParam()
google.sendMessage('雨、降ってきたみたいですよ.')"""

# mariadb getDataテスト.
# agent = mariaDbAgent()
# res = agent.getData(cols=['type', 'subtype', 'datetime', 'data'], w_column=['subtype'], w_value=['current_temp'], order='datetime', by='desc')
# print(res)
# print(len(res))
# data_j = json.loads(res[0][3])
# print(type(data_j))

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

# environment logger  recordRainテスト.
# el = environmentLogger()
# el.recordRain()

# yahooAPIテスト.
# agent = yahooApiAgent()
# agent.getRainLevel()

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

# db select test
db = mariaDbAgent()
result = db.selectCount([db.COL_SUBTYPE], ['test'])
print(result)

# db insert test
result = db.setEventData('test', 'test', None, None, {'message': 'this is test data'})
print(result)