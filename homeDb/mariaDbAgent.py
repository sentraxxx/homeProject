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
    METHOD_SELECT_COUNT = 'select_count'
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
    SUBTYPE_ENV = 'env'                         # homeProjectの環境変数で使用.
    SUBTYPE_GOOGLE_HOME_NOTIFY = 'google_home_notify'   # homeにしゃべらせるalarm.

    # setEnv parameter
    ENV_MAKE_NOTIFY = 'makeNotify'
    ENV_ON = 'on'
    ENV_OFF = 'off'

    # DATA parameter
    DATA_ALARM_STATUS = 'status'
    DATA_ALARM_ENABLE = 'enable'
    DATA_ALARM_DISABLE = 'disable'

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

    def setEnv(self, param, value):

        self.log.info('-- setEnv start')

        sql = 'select data from event where type = \'condition\' and subtype = \'env\''

        connection = mariadb.connect(
            user=self.DB_USER,
            # password = self.DB_PASSWD,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )
        cursor = connection.cursor()

        cursor.execute(sql)
        env_now = cursor.fetchall()
        print(env_now)

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
        """homeDB event tableにSQL直叩き.


        Args:
            sql (str): 叩きたいSQL.
            method (str, optional): mariadb.METHOD_xxxを指定. Defaults to None.

        Returns:
            [int or list]: MEHTODによって返りが異なる. INSERT,UPDATEはrowcount, それ以外はfetchall()の結果.
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

    def getData(self, cols: list, w_column: list, w_value: list, order: str, by: str):
        """home DBのevent tableをselect.

        Args:
            cols (list): 検索カラムのstrリスト. Noneの場合は"*"指定.
            w_column (list): where句のカラムリスト. 指定なしはNone.
            w_value (list): where句のvalueリスト. w_columnと同数必要. 指定なしはNone.
            order (str): order句のカラム名. 指定なしはNone.
            by (str): order句の順序指定. asc(昇順. default), desc(降順), 指定なしはNone. 

        Returns:
            [list]: selectのfetchall()リスト.
        """
        connection = mariadb.connect(
            user=self.DB_USER,
            database=self.DB_DATABASE,
            host=self.DB_HOST
        )

        cursor = connection.cursor()

        # select cols
        if cols is None:
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

        # where句
        where_str = ''
        if w_column is not None:
            first = True
            for i in range(len(w_column)):
                if first:
                    where_str += f' where {w_column[i]}=\'{w_value[i]}\''
                    first = False
                else:
                    where_str += f' and {w_column[i]}=\'{w_value[i]}\''

        # order by
        order_str = ''
        if order is not None:
            order_str += f' order by {order} '
        if by is not None:
            order_str += by

        sql = 'select ' + colstr + ' from event' + where_str + order_str
        self.log.debug(f'sql={sql}')

        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            self.log.debug('sql SELECT executed. sql=', str(sql))

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
            self.log.debug('sql INSERT executed.')
            result_success = cursor.rowcount

        except Exception as e:
            self.log.error(e)
            result_success = False

        cursor.close()
        connection.close()

        return result_success

    def selectCount(self, colomn: list, value: list):
        """dbのレコード数をカウントする.

        Args:
            colomn (list): where句で検索するカラム(str)リスト
            value (list): where句で検索する値(str)リスト. エスケープ処理は気にしなくていい.

        Returns:
            int: selectでヒットした件数.
        """
        where_str = ''
        first = True
        for i in range(len(colomn)):
            if first:
                where_str += f'{colomn[i]}=\'{value[i]}\''
                first = False
            else:
                where_str += f' and {colomn[i]}=\'{value[i]}\''

        sql = f'select count(id) from event where {where_str}'
        print("sql=", sql)

        res = self.execSQL(sql, method=mariaDbAgent.METHOD_SELECT_COUNT)
        count = res[0][0]

        return count

    def setNotifyAlarm(self, text: str) -> bool:
        """google home notifyのアラームセット. 登録後、次回のscheduler周期(最短1分後)に実行される.

        Args:
            text (str): しゃべらせる内容

        Returns:
            bool: 登録結果.
        """
        now = datetime.datetime.now()
        date_format = now.strftime('%Y%m%d%H%M')
        data = {'text': text, mariaDbAgent.DATA_ALARM_STATUS: mariaDbAgent.DATA_ALARM_ENABLE}

        res_success = self.setEventData(type=mariaDbAgent.TYPE_ALARM, subtype=mariaDbAgent.SUBTYPE_GOOGLE_HOME_NOTIFY, time=date_format, place=None, data=data)

        return res_success


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
        """dbのレコード数をカウントする.

        Args:
            colomn (list): where句で検索するカラム(str)リスト
            value (list): where句で検索する値(str)リスト. エスケープ処理は気にしなくていい.

        Returns:
            int: selectでヒットした件数.
        """
        where_str = ''
        first = True
        for i in range(len(colomn)):
            if first:
                where_str += f'{colomn[i]}=\'{value[i]}\''
                first = False
            else:
                where_str += f' and {colomn[i]}=\'{value[i]}\''

        sql = f'select count(id) from event where {where_str}'
        print("sql=", sql)

        res = self.execSQL(sql, method=mariaDbAgent.METHOD_SELECT_COUNT)
        count = res[0][0]

        return count

    def execSQL(self, sql, method=None):
        """homeDB event tableにSQL直叩き.


        Args:
            sql (str): 叩きたいSQL.
            method (str, optional): mariadb.METHOD_xxxを指定. Defaults to None.

        Returns:
            [int or list]: MEHTODによって返りが異なる. INSERT,UPDATEはrowcount, それ以外はfetchall()の結果.
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
                print(f'sql execute succeed. sql={sql}')
                print(f'sql res_rowcount: {res}')
            else:
                cursor.execute(sql)
                res = cursor.fetchall()

            print(f'sql execute succeed. sql={sql}')
            print(f'sql res: {res}')

        except Exception as e:
            print(e)
            res = None

        cursor.close()
        connection.close()

        return res



