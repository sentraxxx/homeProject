from yahooApiAgent import yahooApiAgent
from raspberryPiAgent import raspUtil
from openWeatherAgent import openWeatherAgent
from natureRemo import natureRemoAgent
from homeUtil import handleEnvironment
from homeDb import mariaDbAgent
import logging
import os
import sys
import json
import datetime

sys.path.append('/home/pi/share/dev/homeProject/')


# Environment
LOG_LEVEL = logging.INFO


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

        self.log.info('--- record home_temp(Nature Remo) start.')

        remo = natureRemoAgent()
        temp: float = round(remo.getTemp()['temp'], 1)
        device = 'natureRemo'
        data = {'temp': temp, 'device': device}

        # home_temp(natureRemo) record登録
        mdb = mariaDbAgent()
        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_HOME_TEMP, None, self.place, data)

        if result_success is not None:
            self.log.info('record home_temp succeed.')
        else:
            self.log.error('record home_temp failed.')

        # current_home_temp(natureRemo)アップデート.
        where_type = mdb.TYPE_CONDITION
        where_subtype = mdb.SUBTYPE_CURRENT_HOME_TEMP
        date_format = datetime.datetime.now().strftime('%Y%m%d%H%M')
        data_j = json.dumps(data)
        values = f'datetime = \'{date_format}\', data = \'{data_j}\''

        result_success = mdb.updateData(value=values, type=where_type, subtype=where_subtype)

        if result_success is not None:
            self.log.info('update current_home_temp succeed.')
        else:
            self.log.error('update current_home_temp failed.')

        self.log.info('--- record home_temp end.')

        return

    def recordWeather(self):

        self.log.info('--- record Weather(OpentWeather API) start.')

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

        if result_success is not None:
            self.log.info('record current_weather succeed.')
        else:
            self.log.error(
                'record current_weather failed.')

        # Update Current Weather.
        data_j = json.dumps(data)
        value = f"datetime = {date_format}, data=\'{data_j}\'"
        where_type = mdb.TYPE_CONDITION
        where_subtype = mdb.SUBTYPE_CURRENT_WEATHER

        result_success = mdb.updateData(
            value=value, type=where_type, subtype=where_subtype)

        if result_success is not None:
            self.log.info('update current_weather succeed.')
        else:
            self.log.error('update current_weather failed.')

        # Record temp DB Insert.
        temp = round(currentj['temp'], 1)
        data = {'temp': temp, 'device': 'OpenWeatherAPI'}

        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_TEMP, date_format, self.place, data)

        if result_success is not None:
            self.log.info('record temp succeed.')
        else:
            self.log.error('record temp failed.')

        # Update current_temp
        where_type = mdb.TYPE_CONDITION
        where_subtype = mdb.SUBTYPE_CURRENT_TEMP
        data_j = json.dumps(data)
        value = f"datetime={date_format}, data=\'{data_j}\'"

        result_success = mdb.updateData(
            value=value, type=where_type, subtype=where_subtype)

        if result_success is not None:
            self.log.info('update temp succeed.')
        else:
            self.log.error(
                'update temp failed.')

        self.log.info('--- record Weather end.')

    def recordRain(self):

        self.log.info('--- record Rain(YahooAPI) start.')

        agent = yahooApiAgent()
        weather_list = agent.getRainLevel()

        current_j = {'device': 'YahooAPI'}
        record_j = {'device': 'YahooAPI'}

        mdb = mariaDbAgent()

        return

    def recordRaspberryPiTemp(self):

        self.log.info('--- record raspberrypi cpu_temp start.')

        agent = raspUtil()
        cputemp = agent.getCpuTemp()
        data = {'cpu_temp': cputemp, 'device': 'vcgencmd'}
        now_date = datetime.datetime.now()
        date_format = datetime.datetime.strftime(now_date, '%Y%m%d%H%M')

        self.log.debug(f'start record RapberryPiTemp. data={data}')

        mdb = mariaDbAgent()
        result_success = mdb.setEventData(
            type=mdb.TYPE_RECORD, subtype=mdb.SUBTYPE_RASPI_CPU_TEMP, time=date_format, place=self.place, data=data)

        if result_success is not None:
            self.log.info('record cpu_temp succeed.')
        else:
            self.log.error('record cpu_temp failed.')

        self.log.debug(f'start update RapberryPiTemp. data={data}')
        data_j = json.dumps(data)
        values = f'datetime=\'{date_format}\', data=\'{data_j}\''
        result_success = mdb.updateData(
            value=values, type=mdb.TYPE_CONDITION, subtype=mdb.SUBTYPE_CURRENT_RASPI_CPU_TEMP)

        if result_success is not None:
            self.log.info('update current_cpu_temp update succeed.')
        else:
            self.log.error('update current_cpu_temp update failed.')

        self.log.info('--- record raspberrypi cpu_temp end.')


if __name__ == "__main__":

    el = environmentLogger()
    el.recordHomeTemp()
