import datetime
import logging
import sys

sys.path.append('/home/pi/share/dev/homeProject/')

from homeLogger import environmentLogger
from homeUtil import handleEnvironment

# Environment
LOG_LEVEL = logging.DEBUG


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
        log.info('start every hour task.')

        log.info('end every hour task.')

    # 30分タスク
    if task.IS_EVERY_THIRTY_MIN:
        log.info('start every 30min task.')

        log.info('end every 30min task.')

    # 10分タスク
    if task.IS_EVERY_TEN_MIN:
        log.info('start every 10min task.')

        # natureRemoの室温記録
        el = environmentLogger()
        el.recordHomeTemp()

        log.info('end every 10min task.')

    log.info('scheduler end.')
