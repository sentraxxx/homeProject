import datetime
import logging
import sys
import json


sys.path.append('/home/pi/share/dev/homeProject/')

from homeLogger import environmentLogger
from homeUtil import handleEnvironment, googleHome
from homeDb import mariaDbAgent

# Environment
LOG_LEVEL = logging.INFO


class taskManager:

    def __init__(self):
        self.IS_EVERY_HOUR = False
        self.IS_EVERY_THIRTY_MIN = False
        self.IS_EVERY_TEN_MIN = False

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

        # typeをalarm->alarm_doneに変更. data statusをdisableに変更, last_updateを設定.
        alarm_data[db.DATA_ALARM_STATUS] = db.DATA_ALARM_DISABLE

        now = datetime.datetime.now()
        date_format = now.strftime('%Y%m%d%H%M')
        alarm_data[db.DATA_LAST_UPDATE] = date_format

        # alarm更新
        set_colmns = [db.COL_TYPE, db.COL_DATA]
        set_values = [db.TYPE_ALARM_DONE, json.dumps(alarm_data)]
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
    task.checkTask()

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
        el = environmentLogger()
        el.recordHomeTemp()
        el.recordWeather()
        el.recordRaspberryPiTemp()

        log.info('every 10min task end.')

    # 毎分タスク
    task.execGoogleHomeNotify()

    log.info('scheduler end.')
