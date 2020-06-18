import sys

print(sys.path)
sys.path.append('/home/pi/share/dev/homeProject/')

from natureRemoAgent import natureRemoAgent


a = natureRemoAgent()
res = a.getTemp()

print('temp= ', res['temp'], 'limit= ', res['limit-remain'])




