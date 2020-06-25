import sys
import mariadb
import json
import datetime


print(sys.path)
sys.path.append('/home/pi/share/dev/homeProject/')


class mariaDbAgent:

    TYPE_EVENT = 'event'
    TYPE_ALARM = 'alarm'
    SUBTYPE_HOME_TEMP = 'home_temp'
    SUBTYPE_RAIN_LEVEL = 'rain_level'
    SUBTYPE_TEMP = 'temp'

    def __init__(self, database='homeDB'):

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
        cursor.execute(sql)

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
            #password = self.DB_PASSWD,
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

        query = 'select ' + colstr + ' from ' + table

        cursor.execute(query)

        res = cursor.fetchall()
        print('rowcount: ', cursor.rowcount)

        cursor.close()
        connection.close()

        return res

    def setData(self, table='test', cols=['id', 'name'], values=('null', 'testname')):

        connection = mariadb.connect(
            user=self.DB_USER,
            #password = self.DB_PASSWD,
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

    def setEventData(self, type: str, subtype: str, time: str, place: dict, data: dict,  table='event'):

        # default value set
        if time is None:
            time = datetime.datetime.now().strftime('%Y%m%d%H%M')

        connection = mariadb.connect(
            user=self.DB_USER,
            #password = self.DB_PASSWD,
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
            col_op += col_op + ', data'

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

        print('sql: ', sql)
        res = cursor.execute(sql)

        cursor.close()
        connection.close()

        return res


if __name__ == "__main__":

    db = mariaDbAgent()
    res = db.setEventData(table='event', type=db.TYPE_EVENT, subtype=db.SUBTYPE_HOME_TEMP, data={
                          'temp': 29, 'device': 'natureRemo'}, time=None, place=None)
    res = db.getData(table='event')
    print(res)
