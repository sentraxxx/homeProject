from homeLogger import environmentLogger
from yahooApiAgent import yahooApiAgent
from openWeatherAgent import openWeatherAgent
from accuWeatherAgent import accuWeatherAgent
from homeDb import mariaDbAgent, dbTester
from natureRemo import natureRemoAgent


# yahooAPIテスト.
"""agent = yahooApiAgent()
agent.getRainLevel()"""

# environment Loggerテスト.
agent = environmentLogger()
# el.recordWeather()
# el.recordRaspberryPiTemp()
agent.recordHomeTemp()

"""openweather = openWeatherAgent()
openweather.getCurrentOneCall()
# openweather.getCurrentWeatherByGeo()"""


"""acc = accuWeatherAgent()
acc.getWether()"""

# DB Insertテストモード
"""agent = dbTester()
# print(agent.testSelectCount(['type', 'subtype'], ['condition', 'current_']))
agent.testInsert()"""
