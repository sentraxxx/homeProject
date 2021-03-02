import time
from flask import Flask, send_from_directory, request
import requests
import json
import pychromecast
from voicetext import VoiceText
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import os
import sys
import logging
from gateFunctions import gateFunc

sys.path.append('/home/pi/share/dev/homeProject/src')

# Parameters
LOG_LEVEL = logging.DEBUG

VT_APPKEY = os.environ['VT_APPKEY']
VT_DEFAULT_SPEAKER = 'hikari'
GOOGLE_HOME_IP = '192.168.11.4'
NGROK_ADDR_GET_URL = 'http://127.0.0.1:4040/api/tunnels'
ngrokurl = None
DYNAMODB_TABLE = 'MY_HOST'

# request_parameters
# request_type
REQ_TYPE_INTENT_OSEWA_DETAIL = 'record_osewa_detail'
REQ_TYPE_INTENT_OSEWA_SEARCH = 'search_osewa'

device = pychromecast.Chromecast(GOOGLE_HOME_IP)
print(device)
if not device.is_idle:
    print("killing current running app on Google Home")
    device.quit_app()
    time.sleep(3)
device.wait()


def update_ngrok_url(url):
    t = str(datetime.datetime.now())
    db = boto3.resource('dynamodb')
    table = db.Table('MY_HOST')

    # 最新レコード取得
    print('get latest update record of ngrok..')
    res = table.query(
        KeyConditionExpression=Key('NAME').eq('ngrok'),
        ScanIndexForward=False,
        Limit=1
    )

    # 最新レコードDeisable化
    print('Disable latest ngrok record..')
    res['Items'][0]['STATUS'] = 'Disable'
    table.put_item(
        Item=res['Items'][0]
    )

    # 更新レコード
    print(f'Update ngrok record.. with {url}')
    table.put_item(
        Item={
            'NAME': 'ngrok',
            'HOST': url,
            'UPDATE_DATE': t,
            'STATUS': 'Active'
        }
    )


def get_ngrok_addr():
    global ngrokurl
    if ngrokurl is None:
        r = requests.get(NGROK_ADDR_GET_URL).text
        rj = json.loads(r)
        ngrokurl = rj['tunnels'][0]['public_url']
        print('Get ngrokurl =', ngrokurl)
    return ngrokurl


def make_wav(text, speaker, emotion, emlv, pitch, speed, volume):
    vt = VoiceText(VT_APPKEY).speaker(speaker)
    vt.emotion(emotion, emlv)
    vt.pitch(pitch)
    vt.speed(speed)
    vt.volume(volume)

    log.info('start open wav file')
    with open(f'src/homeGate/cache/{text}_{speaker}_{emotion}_{emlv}_{pitch}_{speed}_{volume}.wav', 'wb')as f:
        f.write(vt.to_wave(text))
        cast(f"{ngrokurl}/cache/{text}_{speaker}_{emotion}_{emlv}_{pitch}_{speed}_{volume}.wav", "audio/wav")

    # google home notify時に実行結果をDB登録したい。なぜか500エラー出るので一旦コメントアウト
    # from homeDb import mariaDbAgent
    #
    # try:
    #     db = mariaDbAgent()
    #     result = db.setEventData(db.TYPE_ALARM_DONE, db.SUBTYPE_GOOGLE_HOME_NOTIFY, None, None, {'message': text})
    #     log.debug(f'set record alarm_done. result={result}')
    # except Exception as e:
    #     log.error(f'record message failed. exepction={e}')

    return


def cast(url, mimetype):
    print(f"wav URL is {url}.")
    mc = device.media_controller
    mc.play_media(url, mimetype)
    mc.block_until_active()
    return


app = Flask(__name__)
app.config['port'] = 8080

# Flaskが設定したRoot Handlerを無効化して
# basicConfigを設定しなおす.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename='./logs/homeProject.log',
    format='[%(asctime)s] %(levelname)s: %(name)s : %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

log = logging.getLogger('homeGate')
log.setLevel(LOG_LEVEL)
log.info('-- flask server with ngrok start.')


@app.route("/")
def index():
    return("hello flask")


@app.route("/cache/<string:path>")
def send_chache(path):
    # print(path)
    return send_from_directory("cache", path)


@app.route("/makeNotify", methods=['POST'])
def makeNotify():
    """google homeにしゃべらせる.
    bodyはjson形式. {'text':'message'}
    パラメータ
     text: must しゃべらせるメッセージ
     id: op
     em: op
     emlv: op
     pitch: op
     speed: op
     volume: op

    Returns:
        json: json body.
    """
    log.info('-- /makeNotify start.')

    data = request.data.decode('utf-8')
    jdata = json.loads(data)
    log.debug(f'request data={jdata}')
    message = jdata['text']

    speakers = ['haruka', 'hikari', 'takeru', 'santa', 'bear']
    emotions = ['happiness', 'anger', 'sadness']

    # set default params
    speaker = speakers[1]
    emotion = emotions[0]
    emlv = 1
    pitch = 100
    speed = 100
    volume = 100

    # set parms from request
    if 'id' in jdata:
        speaker = speakers[jdata['id']]
    if 'em' in jdata:
        emotion = emotions[jdata['em']]
    if 'emlv' in jdata:
        emlv = jdata['emlv']
    if 'pitch' in jdata:
        pitch = jdata['pitch']
    if 'speed' in jdata:
        speed = jdata['speed']
    if 'volume' in jdata:
        volume = jdata['volume']

    log.debug(f'speak param: message={message}, speaker={speaker}, emotion={emotion}, emlv={emlv}, pitch={pitch}, speed={speed}, volume={volume}')

    make_wav(message, speaker, emotion, emlv, pitch, speed, volume)

    log.info('--/makeNotify end')

    return {
        'statusCode': 200,
        'body': json.dumps('== RaspberryPi == sent message to googlehomemes')
    }


@app.route("/makeRecord", methods=['POST'])
def makeRecord():
    log.info('-- /makeRecord start.')

    data = request.data.decode('utf-8')
    jdata = json.loads(data)
    log.debug(f'request data={jdata}')

    func = gateFunc()
    request_type = jdata['request_type']
    res_code = 100

    # request type分岐
    if request_type == REQ_TYPE_INTENT_OSEWA_DETAIL:
        res_code = func.setOsewaRecord(jdata['body'])

    log.info('-- /makeRecord end.')

    return {
        'statusCode': res_code,
        'body': json.dumps('== RaspberryPi == create new Record')
    }


@app.route("/searchRecord", methods=['POST'])
def searchRecord():
    log.info('-- /searchRecord start.')

    data = request.data.decode('utf-8')
    jdata = json.loads(data)
    log.debug(f'request data={jdata}')

    res_code = 200
    res_text = '開発中'

    # request type分岐
    if jdata['request_type'] == REQ_TYPE_INTENT_OSEWA_SEARCH:
        func = gateFunc()
        res_text = func.searchOsewaRecord(jdata['body'])
        log.debug(f'res_text= {res_text}, type={type(res_text)}')

    log.info('-- /searchRecord end.')

    return {
        'statusCode': res_code,
        'body': res_text
    }


# main script
u = get_ngrok_addr()
update_ngrok_url(u)
app.run()
