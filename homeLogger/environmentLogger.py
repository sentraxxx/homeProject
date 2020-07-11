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

        result_success = mdb.updateConditionData(value=values, type=where_type, subtype=where_subtype)

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

        result_success = mdb.updateConditionData(
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

        result_success = mdb.updateConditionData(
            value=value, type=where_type, subtype=where_subtype)

        if result_success is not None:
            self.log.info('update temp succeed.')
        else:
            self.log.error(
                'update temp failed.')

        self.log.info('--- record Weather end.')

    def recordRain(self):
        """yahooAPIで取得した降水量情報(過去1時間〜50分後まで5分毎)を記録する.
        取得した時刻ごとにRecord記録.
        現在時刻(forecastの一番最初)はConditionとして登録.
        
        Record(rain)記録.
        該当時刻がなければ新規Record作成.(基本的にforecastが登録される.)
        observationデータ: data時刻でdatetimeを検索.
                          該当時刻のRecord dataにobserbasionがなければ追加.
        forecastデータ: data時刻でdatetimeを検索.
                      該当時刻のRecord dataにforecastデータを追加.

        Condition(current_rain)記録.
        取得したデータの最初のforecastデータで更新する.(observationだとおそすぎる)


        {observation: x.xx,
         forecast:[
             (取得時刻1: x.xx),
             (取得時刻2: x.xx),
             ...
         ],
         device: YahooAPI 
        }
        """
        self.log.info('--- record Rain(YahooAPI) start.')

        agent = yahooApiAgent()
        weather_list = agent.getRainLevel()
        get_date = datetime.datetime.now().strftime('%Y%m%d%H%M')

        db = mariaDbAgent()

        # weather_listを回しながらDB登録.
        check_forecast = True
        for weather in weather_list:

            # 該当時刻のデータ取得.
            rain_date = weather['Date']
            cols = [db.COL_ID, db.COL_DATA]
            w_columns = [db.COL_TYPE, db.COL_SUBTYPE, db.COL_DATETIME]
            w_values = [db.TYPE_RECORD, db.SUBTYPE_RAIN_LEVEL, rain_date]
            exist_record = db.getData(cols, w_columns, w_values, None, None)
            self.log.debug(f'get Record(rain_level) at Datetime={rain_date} record={exist_record}')

            # 初回登録判定
            newRecord = True if len(exist_record) == 0 else False

            # 登録データ
            place = {'latitude': os.environ['GEO_LATITUDE'], 'longitude': os.environ['GEO_LONGITUDE']}

            # 新規レコード登録
            if newRecord:

                new_data_j = {}

                if weather['Type'] == 'observation':
                    new_data_j['observation'] = weather['Rainfall']
                    new_data_j['forecast'] = []
                else:
                    new_data_j['observation'] = 'None'
                    new_data_j['forecast'] = [[get_date, weather['Rainfall']]]

                new_data_j['device'] = 'YahooAPI'

                # レコード登録
                result = db.setEventData(db.TYPE_RECORD, db.SUBTYPE_RAIN_LEVEL, rain_date, place, new_data_j)
                if result:
                    # self.log.info('new rain_level record insert succeed.')
                    pass
                else:
                    self.log.error('new rain_level record insert failed.')

            # 既存レコード更新
            else:

                update_id = exist_record[0][0]
                update_data = json.loads(exist_record[0][1])

                if weather['Type'] == 'observation':

                    update_data['observation'] = weather['Rainfall']

                else:
                    update_data['forecast'].append([get_date, weather['Rainfall']])

                # 登録データ
                place = {os.environ['GEO_LATITUDE'], os.environ['GEO_LONGITUDE']}

                set_columns = [db.COL_DATA]
                set_values = [json.dumps(update_data)]
                w_columns = [db.COL_ID]
                w_values = [update_id]

                result = db.updateData(set_columns, set_values, w_columns, w_values)
                if result:
                    self.log.debug(f'update Record(rain_level) succeed. target_datetime: {rain_date}')
                else:
                    self.log.error('update Record(rain_level) failed.')

            # 最初のforecast(判定) -> Condition登録
            setCondition = False
            if check_forecast:

                # 最初にforecastを見つけたらsetCondition実行
                # check forecast終了.
                self.log.debug(f'weather type= {weather["Type"]}')
                if weather['Type'] == 'forecast':
                    setCondition = True
                    check_forecast = False

            # Condition更新 -> forecast check off
            if setCondition:
                self.log.info('update current_rain_level start.')

                update_data = json.dumps({'Rainfall': weather['Rainfall'], 'device': 'YahooAPI'})

                condition = db.selectCount([db.COL_TYPE, db.COL_SUBTYPE], [db.TYPE_CONDITION, db.SUBTYPE_CURRENT_RAIN_LEVEL])
                if condition == 0:
                    result = db.setEventData(db.TYPE_CONDITION, db.SUBTYPE_CURRENT_RAIN_LEVEL, get_date, place, update_data)
                    if result:
                        self.log.info('first Condition(current_rain_level) insert succeed.')
                    else:
                        self.log.error('first Condition(current_rain_level) insert failed.')

                else:
                    set_columns = [db.COL_DATETIME, db.COL_DATA]
                    set_values = [get_date, update_data]
                    w_columns = [db.COL_TYPE, db.COL_SUBTYPE]
                    w_values = [db.TYPE_CONDITION, db.SUBTYPE_CURRENT_RAIN_LEVEL]

                    result = db.updateData(set_columns, set_values, w_columns, w_values)
                    if result:
                        self.log.debug('update current_rain_level succeed.')
                    else:
                        self.log.error('update current_rain_level failed.')

                check_forecast = False

        self.log.info('--- record Rain(YahooAPI) end.')

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
        result_success = mdb.updateConditionData(
            value=values, type=mdb.TYPE_CONDITION, subtype=mdb.SUBTYPE_CURRENT_RASPI_CPU_TEMP)

        if result_success is not None:
            self.log.info('update current_cpu_temp update succeed.')
        else:
            self.log.error('update current_cpu_temp update failed.')

        self.log.info('--- record raspberrypi cpu_temp end.')


if __name__ == "__main__":

    el = environmentLogger()
    el.recordHomeTemp()
