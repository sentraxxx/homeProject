import datetime
import logging
import sys
import json


sys.path.append('/home/pi/share/dev/homeProject/')

from homeLogger import environmentLogger
from homeUtil import handleEnvironment, googleHome, ifttt
from homeDb import mariaDbAgent

# Environment
LOG_LEVEL = logging.INFO


class taskManager:

    def __init__(self):

        # 定期タスク実行判定
        self.IS_EVERY_HOUR = False
        self.IS_EVERY_THIRTY_MIN = False
        self.IS_EVERY_TEN_MIN = False
        self.IS_EVERY_FIVE_MIN = False

        # 時間帯判定
        self.IS_DAYTIME_WORK = False
        self.IS_SLEEP_TIME = False

        # taskで保持するデータ.
        self.rain_level_before = float(0)

    def checkTask(self):
        t = datetime.datetime.now()
        print(t.minute)

        if t.minute == 0:
            self.IS_EVERY_HOUR = True
            log.debug('this is every hour schedule')

        if t.minute == 0 or t.minute == 30:
            self.IS_EVERY_THIRTY_MIN = True
            log.debug('this is every 30min schedule')

        if t.minute % 10 == 0:
            self.IS_EVERY_TEN_MIN = True
            log.debug('this is every 10min schedule')

        if t.minute % 5 == 0:
            self.IS_EVERY_FIVE_MIN = True
            log.debug('this is every 5min schedule')

        if t.hour > 9 and t.hour < 18:
            self.IS_DAYTIME_WORK = True
            log.debug('IS_DAYTIME_WORK = True')

        if t.hour > 0 and t.hour < 7:
            self.IS_SLEEP_TIME = True
            log.debug('IS_SLEEP_TYME = True')

    def checkRainCondition(self):

        db = mariaDbAgent()
        cols = [db.COL_DATA]
        w_columns = [db.COL_TYPE, db.COL_SUBTYPE]
        w_values = [db.TYPE_CONDITION, db.SUBTYPE_CURRENT_RAIN_LEVEL]
        result = db.getData(cols, w_columns, w_values, None, None)

        rain_level_after = float(json.loads(result[0][0])['Rainfall'])
        log.debug(f'rain level(after) = {rain_level_after}')

        try:
            if self.rain_level_before == 0 and rain_level_after > 0:
                log.info(f'** rain level alarm set. {self.rain_level_before} to {rain_level_after}')
                agent = ifttt()
                message = f'雨が振りそうですよー. 予想降水量は {rain_level_after}'
                agent.sendMessage(message)

                if self.IS_DAYTIME_WORK or self.IS_SLEEP_TIME:
                    pass
                else:
                    db.setNotifyAlarm(message)

        except Exception as e:
            log.debug(e)

        return

    def setRainCondition(self) -> float:

        db = mariaDbAgent()
        cols = [db.COL_DATA]
        w_columns = [db.COL_TYPE, db.COL_SUBTYPE]
        w_values = [db.TYPE_CONDITION, db.SUBTYPE_CURRENT_RAIN_LEVEL]
        result = db.getData(cols, w_columns, w_values, None, None)

        rain_level = float(json.loads(result[0][0])['Rainfall'])
        log.debug(f'rain level(before) = {rain_level}')

        self.rain_level_before = rain_level

        return rain_level

    def execGoogleHomeNotify(self):
        """event tableのalarm (subtype: google_home_notify)の最古、かつ status=enableを検索し、googlhomeでしゃべらせる.通知後はalarmのstatusをdisableに変更する.
        """

        log.info('-- google_Home_Notify start')

        # mariadbから一番古いalarm: google_home_notify を取得
        # id取得、テキスト取得
        db = mariaDbAgent()
        cols = [db.COL_ID, db.COL_DATA]
        w_column = [db.COL_TYPE, db.COL_SUBTYPE]
        w_value = [db.TYPE_ALARM, db.SUBTYPE_GOOGLE_HOME_NOTIFY]

        alarm = db.getData(cols, w_column, w_value, None, None)
        if len(alarm) == 0:
            log.info('no alarm to notify.')
            log.info('-- google home notify end.')
            return

        log.debug(f'alarm= {alarm}')

        alarm_id = alarm[0][0]
        alarm_data = json.loads(alarm[0][1])

        # しゃべらせる
        google = googleHome()
        message = alarm_data['text']
        code = google.sendMessage(message)

        if code == 200:
            log.info('send message to GoogleHome succeed.')
        else:
            log.warning(f'send message to GoogleHome failed. code={code}.')
            log.warning('-- google_Home_Notify abort.')
            return

        if code == 200:
            # typeをalarm->alarm_doneに変更. data statusをdisableに変更, last_updateを設定.
            alarm_data[db.DATA_ALARM_STATUS] = db.DATA_ALARM_DISABLE

            now = datetime.datetime.now()
            date_format = now.strftime('%Y%m%d%H%M')
            alarm_data[db.DATA_LAST_UPDATE] = date_format

            # alarm更新
            set_colmns = [db.COL_TYPE, db.COL_DATA]
            set_values = [db.TYPE_ALARM_DONE, json.dumps(alarm_data, ensure_ascii=False)]
            w_columns = [db.COL_ID]
            w_values = [str(alarm_id)]
            db.updateData(set_colmns, set_values, w_columns, w_values)

        log.info('-- google_Home_Notify end.')

        return


if __name__ == "__main__":

    # set Log
    handleEnvironment.initialize()
    log = logging.getLogger('homeScheduler')
    log.setLevel(LOG_LEVEL)
    log.info('scheduler start.')

    task = taskManager()
    el = environmentLogger()

    # 実行前処理
    task.checkTask()
    task.setRainCondition()

    # 毎時タスク
    if task.IS_EVERY_HOUR:
        log.info('every hour task start.')

        log.info('every hour task end.')

    # 30分タスク
    if task.IS_EVERY_THIRTY_MIN:
        log.info('every 30min task start.')

        log.info('every 30min task end.')

    # 10分タスク
    if task.IS_EVERY_TEN_MIN:
        log.info('every 10min task start.')

        # natureRemoの室温記録
        el.recordHomeTemp()
        el.recordWeather()
        el.recordRaspberryPiTemp()

        log.info('every 10min task end.')

    # 5分タスク
    if task.IS_EVERY_FIVE_MIN:
        log.info('every 5min task start.')

        el.recordRain()
        task.checkRainCondition()

        log.info('every 5min task end.')

    # 毎分タスク
    # task.execGoogleHomeNotify()

    # Schaduler TEST用
    try:
        pass
    except Exception as e:
        log.error(e)

    log.info('scheduler end.')
