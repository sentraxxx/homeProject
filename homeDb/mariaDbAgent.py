from homeUtil import handleEnvironment
import sys
import mariadb
import json
import datetime
import logging

sys.path.append('/home/pi/share/dev/homeProject/')


# Environment.
LOG_LEVEL = logging.DEBUG


class mariaDbAgent:
    """基本的なDBアクセスを提供. Method毎にConnection, Cursorを生成/終了する.

    Returns:
        インスタンス: mariaDBアクセスのためのインスタンス
    """

    TYPE_RECORD = 'record'
    TYPE_ALARM = 'alarm'
    TYPE_CONDITION = 'condition'
    SUBTYPE_HOME_TEMP = 'home_temp'
    SUBTYPE_RAIN_LEVEL = 'rain_level'
    SUBTYPE_TEMP = 'temp'
    SUBTYPE_CURRENT_WEATHER = 'current_weather'
    SUBTYPE_CURRENT_TEMP = 'current_temp'
    SUBTYPE_CURRENT_WIND = 'current_wind'
    SUBTYPE_CURRENT_TEMP = 'current_temp'

    def __init__(self, database='homeDB'):

        # Logset
        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

        # DBset
        self.DB_HOST = 'localhost'
        self.DB_USER = 'root'
        self.DB_DATABASE = database

        return

    def execSQL(self, sql, table='test'):
        """sqlを直叩き。なんでも入力できるのでレスポンスなし

        Args:
            sql ([type]): [description]
            table (str, optional): [description]. Defaults to 'test'.
        """

        connection = mariadb.connect(
            user=self.DB_USER,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )

        cursor = connection.cursor()

        try:
            cursor.execute(sql)

        except Exception as e:
            self.log.err(e)

        return

    def getData(self, table='test', cols=['*']):
        """tableのcols要素を検索.

        Args:
            table (str, optional): 対象テーブル. Defaults to 'test'.
            cols (list, optional): 検索の列名リスト. Defaults to ['*'].

        Returns:
            list: 検索行のリスト.1行1タプルに格納される.
        """

        connection = mariadb.connect(
            user=self.DB_USER,
            # password = self.DB_PASSWD,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )

        cursor = connection.cursor()

        if cols[0] == '*':
            colstr = '*'

        else:
            f_first = True
            colstr = ''
            for c in cols:
                if f_first:
                    colstr += c
                    f_first = False
                else:
                    colstr = colstr + ', ' + c

        print('col:', colstr)

        sql = 'select ' + colstr + ' from ' + table

        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            set.log.info('sql SELECT executed. sql=', str(sql))

        except Exception as e:
            self.log.err(e)
            res = None

        cursor.close()
        connection.close()

        return res

    def setData(self, table='test', cols=['id', 'name'], values=('null', 'testname')):

        connection = mariadb.connect(
            user=self.DB_USER,
            # password = self.DB_PASSWD,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )

        cursor = connection.cursor()

        colstr = ''
        f_first = True
        for c in cols:
            if f_first:
                colstr += c
                f_first = False
            else:
                colstr = colstr + ', ' + c
        print('col: ', colstr)

        placeholder = ''
        f_first = True
        for p in range(len(cols)):
            if f_first:
                placeholder += '?'
                f_first = False
            else:
                placeholder = placeholder + ', ?'

        sql = 'insert into ' + table + \
            ' (' + colstr + ') values (' + placeholder + ')'
        print('sql: ', sql)
        print('values:', values)
        res = cursor.execute(sql, values)

        cursor.close()
        connection.close()

        return res

    def getConnection(self):
        """mariaDBを直接操作する場合に使用するconnection.
        connection.Cursor()でcursorをつかみ、sql操作する。
        https://github.com/mariadb-corporation/mariadb-connector-python

        Returns:
            mariadb.connection: homeDBへのconnection.
        """

        connection = mariadb.connect(
            user=self.DB_USER,
            # password = self.DB_PASSWD,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )

        return connection

    def setEventData(self, type: str, subtype: str, time: str, place: dict, data: dict, table='event'):
        """homeDBにEventデータを登録する。

        Args:
            type (str): event|alarm. mariadbAgent.TYPE_xxx
            subtype (str): home_temp|temp|... mariadbAgent.SUBTYPE_xxx
            time (str): YYYYMMDDhhmi形式. Noneの場合現在時刻が設定される。
            place (dict): JSON形式の位置情報. latitude(経度 -90~90), longitude(経度 -180~180).
            data (dict): TYPE,SUBTYPE毎に定義したデータ形式(JSON).
            table (str, optional): 'event'固定. Defaults to 'event'.

        Returns:
            result_success(bool): success=True. SQL error=False.
        """

        # default value set
        if time is None:
            time = datetime.datetime.now().strftime('%Y%m%d%H%M')

        connection = mariadb.connect(
            user=self.DB_USER,
            # password = self.DB_PASSWD,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )

        cursor = connection.cursor()

        # base
        sql = 'insert into ' + table

        # must col
        sql += ' (type, subtype, datetime'

        # optional col
        col_op = ''
        if place:
            col_op += ', place'
        if data:
            col_op += ', data'

        # close col
        sql += col_op + ') '

        # set must values
        sql += 'values (\'' + type + '\',\'' + subtype + '\',\'' + time + '\''

        # set optional values
        op_values = ''
        if place:
            op_values += ',\'' + json.dumps(place) + '\''
        if data:
            op_values += ',\'' + json.dumps(data) + '\''

        # close optional values
        sql += op_values + ')'

        try:
            self.log.info('sql INSERT. sql=' + str(sql))
            cursor.execute(sql)
            self.log.info('sql INSERT executed.')
            result_success = True

        except Exception as e:
            self.log.error(e)
            result_success = False

        cursor.close()
        connection.close()

        return result_success
