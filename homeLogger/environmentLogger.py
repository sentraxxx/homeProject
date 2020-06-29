import logging
import os
import sys

sys.path.append('/home/pi/share/dev/homeProject/')

from homeDb import mariaDbAgent
from homeUtil import handleEnvironment
from natureRemo import natureRemoAgent

# Environment
LOG_LEVEL = logging.DEBUG


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

        print(self.place)

        return

    def recordHomeTemp(self):

        self.log.info('start recordHomeTemp')

        remo = natureRemoAgent()
        temp = round(remo.getTemp()['temp'], 1)
        device = 'natureRemo'

        self.log.info('get home_temp from natureremo: ' + str(temp))

        data = {'temp': temp, 'device': device}

        mdb = mariaDbAgent()
        result_success = mdb.setEventData(
            mariaDbAgent.TYPE_RECORD, mariaDbAgent.SUBTYPE_HOME_TEMP, None, self.place, data)

        if result_success:
            self.log.info('record home_temp event succeed.')
        else:
            self.log.error('record home_temp event failed.')

        return


if __name__ == "__main__":

    el = environmentLogger()
    el.recordHomeTemp()
