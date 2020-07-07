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

        self.log.info('start record HomeTemp')

        remo = natureRemoAgent()
        temp: float = round(remo.getTemp()['temp'], 1)
        device = 'natureRemo'
        data = {'temp': temp, 'device': device}

        # home_temp(natureRemo) record登録
        mdb = mariaDbAgent()
        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_HOME_TEMP, None, self.place, data)

        if result_success is not None:
            self.log.info('record home_temp event succeed.')
        else:
            self.log.error('record home_temp event failed.')

        # current_home_temp(natureRemo)アップデート.
        where_type = mdb.TYPE_CONDITION
        where_subtype = mdb.SUBTYPE_CURRENT_HOME_TEMP
        date_format = datetime.datetime.now().strftime('%Y%m%d%H%M')
        data_j = json.dumps(data)
        values = f'datetime = \'{date_format}\', data = \'{data_j}\''

        result_success = mdb.updateData(value=values, type=where_type, subtype=where_subtype)

        if result_success is not None:
            self.log.info('record current_home_temp event succeed.')
        else:
            self.log.error('record current_home_temp event failed.')

        return

    def recordWeather(self):

        self.log.info('start record Weather')

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
        self.log.info('start Condition OpenWeatherAPI:Current_Weather.')
        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_WEATHER, date_format, self.place, data)

        if result_success is not None:
            self.log.info('Condition OpenWeatherAPI:Current_Weather inserted.')
        else:
            self.log.error(
                'Condition OpenWeatherAPI:Current_Weather insert failed.')

        # Update Current Weather.
        self.log.info('start update current_weather.')
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
        self.log.info('start Record OpenWeatherAPI:Temp.')
        temp = round(currentj['temp'], 1)
        data = {'temp': temp, 'device': 'OpenWeatherAPI'}

        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_TEMP, date_format, self.place, data)

        if result_success is not None:
            self.log.info('Record OpenWeatherAPI:Temp inserted.')
        else:
            self.log.error('Record OpenWeatherAPI:Temp insert failed.')

        # Update current_temp
        self.log.info('start Condition OpenWeatherAPI:Current_Temp.')
        where_type = mdb.TYPE_CONDITION
        where_subtype = mdb.SUBTYPE_CURRENT_TEMP
        data_j = json.dumps(data)
        value = f"datetime={date_format}, data=\'{data_j}\'"

        result_success = mdb.updateData(
            value=value, type=where_type, subtype=where_subtype)

        if result_success is not None:
            self.log.info('Condition OpenWeatherAPI:Current_Temp Updated.')
        else:
            self.log.error(
                'Condition OpenWeatherAPI:Current_Temp Update failed.')

    def recordRain(self):

        self.log.info('start record Rain from YahooAPI')

        agent = yahooApiAgent()
        weather_list = agent.getRainLevel()

        current_j = {'device': 'YahooAPI'}
        record_j = {'device': 'YahooAPI'}

        mdb = mariaDbAgent()

        return

    def recordRaspberryPiTemp(self):

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
            self.log.info('Record Cpu_Temp insert succeed.')
        else:
            self.log.error('Record Cpu_Temp insert failed.')

        self.log.debug(f'start update RapberryPiTemp. data={data}')
        data_j = json.dumps(data)
        values = f'datetime=\'{date_format}\', data=\'{data_j}\''
        result_success = mdb.updateData(
            value=values, type=mdb.TYPE_CONDITION, subtype=mdb.SUBTYPE_CURRENT_RASPI_CPU_TEMP)

        if result_success is not None:
            self.log.info('Update current_cpu_temp update succeed.')
        else:
            self.log.error('Update current_cpu_temp update failed.')


if __name__ == "__main__":

    el = environmentLogger()
    el.recordHomeTemp()
