import subprocess
import logging
from homeUtil import handleEnvironment

LOG_LEVEL = logging.DEBUG


class raspUtil:

    def __init__(self):

        handleEnvironment.initialize()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)

    def getCpuTemp(self):

        cmd = 'vcgencmd measure_temp'
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = result.communicate()
        sp_temp = stdout.split('=')
        cpuTemp = int(sp_temp[1])

        return cpuTemp
