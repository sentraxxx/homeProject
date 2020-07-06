import logging
import os
import sys
import json
import datetime

sys.path.append('/home/pi/share/dev/homeProject/')

from homeDb import mariaDbAgent
from homeUtil import handleEnvironment
from natureRemo import natureRemoAgent
from openWeatherAgent import openWeatherAgent
from raspberryPiAgent import raspUtil

# Environment
LOG_LEVEL = logging.DEBUG


class environmentLogger:

    def __init__(self):

        # Logset
        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)
        self.log.debug('environmentLogger start.')

        # default data.
        try:
            self.place = {
                'latitude': os.environ['GEO_LATITUDE'], 'longitude': os.environ['GEO_LONGITUDE']}

        except Exception as e:
            self.log.error('set place error.')
            self.log.debug(e)

        return

    def recordHomeTemp(self):

        self.log.info('start recordHomeTemp')

        remo = natureRemoAgent()
        temp: float = round(remo.getTemp()['temp'], 1)
        device = 'natureRemo'

        self.log.info('get home_temp from natureremo: ' + str(temp))

        data = {'temp': temp, 'device': device}

        mdb = mariaDbAgent()
        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_HOME_TEMP, None, self.place, data)

        if result_success:
            self.log.info('record home_temp event succeed.')
        else:
            self.log.error('record home_temp event failed.')

        return

    def recordWeather(self):

        agent = openWeatherAgent()
        res = agent.getCurrentOneCall()
        self.log.debug(f'openWeatherAPI. OneCall res = {res}')
        resj = json.loads(res)

        currentj = resj['current']
        self.log.debug(currentj)

        hourlyj = resj['hourly']
        self.log.debug(hourlyj)

        dailyj = resj['daily']
        self.log.debug(dailyj)

        # current weater
        date_unix = currentj['dt']
        date = agent.utcToJst(date_unix)
        date_format = datetime.datetime.strftime(date, '%Y%m%d%H%M')

        currentj['date'] = str(date_format)
        currentj['device'] = 'OpenWeatherAPI'

        data = currentj

        # Record Weather DB insert
        mdb = mariaDbAgent()
        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_WEATHER, date_format, self.place, data)

        if result_success:
            self.log.info('Condition OpenWeatherAPI:Current_Weather inserted.')
        else:
            self.log.error('Condition OpenWeatherAPI:Current_Weather insert failed.')

        # Update Current Weather.
        value = f'datetime = {date_format}, data={data}'
        where_type = mdb.TYPE_CONDITION
        where_subtype = mdb.SUBTYPE_CURRENT_WEATHER

        result_success = mdb.updateData(value=value, type=where_type, subtype=where_subtype)

        if result_success:
            self.log.info('update current_weather succeed.')
        else:
            self.log.error('update current_weather failed.')

        return

        # Record temp DB Insert.
        temp = round(currentj['temp'], 1)

        data = {'temp': temp, 'device': 'OpenWeatherAPI'}

        result_success = mdb.setEventData(mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_TEMP, date_format, self.place, data)

        if result_success:
            self.log.info('Record OpenWeatherAPI:Temp inserted.')
        else:
            self.log.error('Record OpenWeatherAPI:Temp insert failed.')

        # Update current_temp
        where_type = mdb.TYPE_CONDITION
        where_subtype = mdb.SUBTYPE_CURRENT_TEMP
        value = f'datetime={date_format}, data={data}'

        result_success = mdb.updateData(value=value, type=where_type, subtype=where_subtype)

        if result_success:
            self.log.info('Condition OpenWeatherAPI:Current_Temp Updated.')
        else:
            self.log.error('Condition OpenWeatherAPI:Current_Temp Update failed.')

    def recordRaspberryPiTemp():

        agent = raspUtil()
        cputemp = agent.getCpuTemp()

        data = {'cpu_temp': cputemp, 'device': 'vcgencmd'}



        pass


if __name__ == "__main__":

    el = environmentLogger()
    el.recordHomeTemp()
