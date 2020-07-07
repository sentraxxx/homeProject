from homeUtil import handleEnvironment
import mariadb
import sys
import json
import datetime
import logging

sys.path.append('/home/pi/share/dev/homeProject/')

# Environment.
LOG_LEVEL = logging.INFO


class mariaDbAgent:
    """基本的なDBアクセスを提供. Method毎にConnection, Cursorを生成/終了する.

    Returns:
        インスタンス: mariaDBアクセスのためのインスタンス
    """

    METHOD_INSERT = 'insert'
    METHOD_SELECT = 'select'
    METHOD_UPDATE = 'udpate'
    METHOD_COUNT = 'count'

    TYPE_RECORD = 'record'                      # 継続的な記録
    TYPE_ALARM = 'alarm'                        # 何らかのアクションを起こすトリガ
    TYPE_CONDITION = 'condition'                # 現在の状況
    SUBTYPE_HOME_TEMP = 'home_temp'             # nature Remoから取得する室温
    SUBTYPE_RAIN_LEVEL = 'rain_level'           # Yahoo APIから取得する降水量
    SUBTYPE_TEMP = 'temp'                       # 外気温
    SUBTYPE_WEATHER = 'weather'                 # 天気全般
    SUBTYPE_RASPI_CPU_TEMP = 'cpu_temp'         # RaspberryPiのCPU温度
    SUBTYPE_CURRENT_HOME_TEMP = 'current_home_temp'     # 現在の室温
    SUBTYPE_CURRENT_WEATHER = 'current_weather'     # 現在の天気 conditionで記録
    SUBTYPE_CURRENT_TEMP = 'current_temp'       # 現在の外気温　conditionで記録
    SUBTYPE_CURRENT_WIND = 'current_wind'       # 現在の風 conditionで記録
    SUBTYPE_CURRENT_RAIN = 'current_rain'       # 現在の降水量　conditionで記録
    SUBTYPE_CURRENT_RASPI_CPU_TEMP = 'current_cpu_temp'     # 現在のRaspberryPiのCPU温度 conditionで記録

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

    def updateData(self, value: str, type, subtype):
        """event tableのアップデートを行う。主にcurrentのdata更新を想定.

        Args:
            value (str): 更新する値.data, datetimeなど.
            type (str): 対象のTYPE. mariadb.TYPE...
            subtype (str): 対象のSUBTYPE. mariadb.SUBTYPE...

        Returns:
            [list]: sql実行結果.fetchall()のレスポンス. タプルのリスト.
        """
        self.log.debug(f'start mariadb update. value={value}, type={type}, subtype={subtype}')

        sql = f'update event set {value} where type=\'{type}\' and subtype=\'{subtype}\''
        self.log.debug(f'sql= {sql}')

        try:
            res = self.execSQL(sql, method=mariaDbAgent.METHOD_UPDATE)
            self.log.debug('update succeed.')

        except Exception as e:
            res = None
            self.log.error(e)

        return res

    def execSQL(self, sql, method=None):
        """sqlを直叩き。なんでも入力できるのでレスポンスなし

        Args:
            sql ([type]): [description]
            method (str, optional): mariadb.METHOD...の値.現状はINSERTだけ有効
        """

        connection = mariadb.connect(
            user=self.DB_USER,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )

        cursor = connection.cursor()

        try:
            if method == mariaDbAgent.METHOD_INSERT or method == mariaDbAgent.METHOD_UPDATE:
                cursor.execute(sql)
                res = cursor.rowcount
            else:
                cursor.execute(sql)
                res = cursor.fetchall()

            self.log.debug(f'sql execute succeed. sql={sql}')
            self.log.debug(f'sql res: {res}')

        except Exception as e:
            self.log.error(e)
            res = None

        cursor.close()
        connection.close()

        return res

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
            set.log.debug('sql SELECT executed. sql=', str(sql))

        except Exception as e:
            self.log.error(e)
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
        self.log.debug(f'sql={sql}')

        try:
            cursor.execute(sql)
            self.log.info('sql INSERT executed.')
            result_success = cursor.rowcount

        except Exception as e:
            self.log.error(e)
            result_success = False

        cursor.close()
        connection.close()

        return result_success


class dbTester:

    def __init__(self, database='homeDB'):

        # DBset
        self.DB_HOST = 'localhost'
        self.DB_USER = 'root'
        self.DB_DATABASE = database

    def testInsert(self):

        sql = 'insert into event (type, subtype, datetime) values(\'test_type\', \'test_subtype\', \'202099990000\')'

        res = self.execSQL(sql, method=mariaDbAgent.METHOD_INSERT)
        print(res)

        return

    def testSelectCount(self, colomn: list, value: list):

        where_str = ' '
        first = True
        for i in range(len(colomn)):
            if first:
                where_str += f'{colomn[i]}=\'{value[i]}\''
                first = False
            else:
                where_str += f'and {colomn[i]}=\'{value[i]}\''

        sql = f'select count(id) from event where {where_str}'

        res = self.execSQL(sql)
        count = res[0][0]

        return count

    def execSQL(self, sql, method=None):
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
            if method == mariaDbAgent.METHOD_INSERT:
                cursor.execute(sql)
                res = cursor.rowcount
                print('insert executed. res=', res)
            else:
                res = cursor.fetchall()
                print('sql executed. res=', res)

        except Exception as e:
            print(e)
            res = False

        cursor.close()
        connection.close()

        return res
