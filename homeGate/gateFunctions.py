import sys
import logging
import datetime

sys.path.append('/home/pi/share/dev/homeProject/')

from homeUtil import handleEnvironment
from homeDb import mariaDbAgent

LOG_LEVEL = logging.INFO


class gateFunc:

    def __init__():
        handleEnvironment.initialize()
        self.log = logging.getLogger('gateFunc')

    def setRecord(self):
        db = mariaDbAgent()

        # subtype toiletに記録
        type = db.TYPE_RECORD
        subtype = db.SUBTYPE_TOILET
        now = datetime.datetime.now()
        date_str = datetime.datetime.now().strftime('%Y%m%d%H%M')


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
