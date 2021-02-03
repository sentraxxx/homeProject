import sys
import logging
import datetime
import json
from dateutil.relativedelta import relativedelta

sys.path.append('/home/pi/share/dev/homeProject/src')

from homeUtil import handleEnvironment
from homeDb import mariaDbAgent

LOG_LEVEL = logging.INFO


class gateFunc:

    def __init__(self):
        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

    def setOsewaRecord(self, data):
        """お世話レコードを追加する. type: record, subtype: osewa

        Args:
            data (json): data列の値.

        Returns:
            int: レスポンスコード. 200 ok, 500 failed.
        """
        self.log.info('-- set osewa_record start')
        db = mariaDbAgent()

        # subtype osewaに記録
        date_str = datetime.datetime.now().strftime('%Y%m%d%H%M')
        is_success = db.setEventData(db.TYPE_RECORD, db.SUBTYPE_OSEWA, date_str, None, data)

        res_code = 100
        if is_success:
            self.log.info('create new record succeed.')
            res_code = 200
        else:
            self.log.error('create new record failed.')
            res_code = 500

        self.log.info('-- set osewa_record end')

        return res_code

    def searchOsewaRecord(self, data):
        """search Osewa intentを受けてデータ検索を行う。

        Args:
            data (dict): 入力パラメータ. when: 検索期間 who, category

        Response:
            res_text(str): サーチ結果
        """
        self.log.info('-- search_osewa_record start')

        # when list
        WHEN_LAST_TIME = '前回'
        WHEN_TODAY = '今日'
        WHEN_THIS_WEEK = '今週'
        WHEN_THIS_MONTH = '今月'
        WHEN_YESTERDAY = '昨日'
        WHEN_LAST_WEEK = '先週'
        WHEN_LAST_MONTH = '先月'


        # db検索
        db = mariaDbAgent()

        type_val = db.TYPE_RECORD
        subtype_val = db.SUBTYPE_OSEWA

        # datetime指定
        now = datetime.datetime.now()

        if data['when'] == WHEN_TODAY:
            attr_datetime = f"like '{now.strftime('%Y%m%d')}%'"
        elif data['when'] == WHEN_YESTERDAY:
            td = datetime.timedelta(days=-1)
            target_date = now + td
            attr_datetime = f"like '{target_date.strftime('%Y%m%d')}%'"
        elif data['when'] == WHEN_THIS_MONTH:
            attr_datetime = f"like '{now.strftime('%Y%m')}%'"
        elif data['when'] == WHEN_LAST_MONTH:
            td = relativedelta(months=-1)
            target_date = now + td
            attr_datetime = f"like '{target_date.strftime('%Y%m')}%'"
        elif data['when'] == WHEN_LAST_TIME:
            attr_datetime = f"like '{now.strftime('%Y')}%'"
        else:
            attr_datetime = f"like '{now.strftime('%Y%m%d')}%'"

        sql = f"select datetime, data from event where type='{type_val}' and subtype='{subtype_val}' and datetime {attr_datetime} order by datetime desc"
        db_result = db.execSQL(sql)

        self.log.debug(f'sql: {sql}')

        # db検索結果の解析
        db_result_count = len(db_result)

        result_count = 0
        result_last = None
        for record in db_result:
            if json.loads(record[1])['who'] != data['who']:
                continue
            if json.loads(record[1])['category'] != data['category']:
                continue
            # 該当レコードの最初(最新)だけ記録
            if result_last is None:
                result_last = record
            # 回数カウント
            result_count += 1

        self.log.debug(f'count= {db_result_count}, result_count= {result_count}, result_last= {result_last}')

        # レスポンス作成
        res_text = '読み込みに失敗しましたー.'
        if result_count == 0:
            if data['when'] == WHEN_LAST_TIME:
                res_text = f"{data['who']}の{data['category']}は、まだ記録されてません. 他になにかしますか？"
            else:
                res_text = f"{data['when']}は、{data['category']}の記録がありません. 別のことを調べますか？"
        else:
            record_date = datetime.datetime.strptime(result_last[0], '%Y%m%d%H%M')
            record_data = json.loads(result_last[1])

            # 最終時間のテキスト作成
            last_date = ''
            td = now - record_date
            if now.date() == record_date.date():
                if td.seconds < 3600:
                    last_date = f'{int(td.seconds/60)}分前'
                else:
                    last_date = f'{int(td.seconds/3600)}時間 {int(td.seconds%3600/60)}分前'
            elif td.days == 1:
                last_date = f'昨日の{record_date.hour}時'
            elif td.days == 2:
                last_date = f'一昨日の{record_date.hour}時'
            else:
                month = record_date.month
                day = record_date.day
                hour = record_date.hour
                last_date = f'{month}月{day}日、{hour}時'

            # レスポンステキスト作成
            if data['when'] == WHEN_LAST_TIME:
                res_text = f"{data['when']}の{data['who']}の{data['category']}は、{last_date}で「{record_data['detail']}」とメモしてます. 他になにか調べますか？"
            else:
                res_text = f"{data['when']}の{data['who']}の{data['category']}は、{result_count}回ありました. 他になにか調べますか？"

        self.log.debug(f'res_text: {res_text}')
        self.log.info('-- search_osewa_record end')

        return res_text

    @staticmethod
    def testfunc():
        handleEnvironment.initialize()
        log = logging.getLogger('Test Func2')
        log.setLevel(LOG_LEVEL)

        log.info('test func2')
        print('test func')

        db = mariaDbAgent()
        db.selectCount([db.COL_TYPE], [db.TYPE_RECORD])

        return
