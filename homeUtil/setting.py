import os
import logging
import sys

sys.path.append('/home/pi/share/dev/homeProject/')


LOG_LEVEL = logging.DEBUG


class handleEnvironment:

    def __init__(self):
        pass

    @staticmethod
    def initialize():

        handleEnvironment.initializeLogging()

        return

    @staticmethod
    def initializeLogging():

        # Create Log Folder
        if os.path.isdir('./logs/'):
            # print('./logs/はあったよ')
            pass
        else:
            os.mkdir('./logs/')
            # print('makeしたつもり')

        # set logging.
        logging.basicConfig(
            filename='./logs/homeProject.log',
            format='[%(asctime)s] %(levelname)s: %(name)s : %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
