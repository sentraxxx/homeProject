import time
from flask import Flask, send_from_directory, request
import requests
import json
import pychromecast
from voicetext import VoiceText
import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime
import os

VT_APPKEY = os.environ['VT_APPKEY']
VT_DEFAULT_SPEAKER = 'hikari'
GOOGLE_HOME_IP = '192.168.11.3'
NGROK_ADDR_GET_URL = 'http://127.0.0.1:4040/api/tunnels'
ngrokurl = None
DYNAMODB_TABLE = 'MY_HOST'

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
        KeyConditionExpression= Key('NAME').eq('ngrok'),
        ScanIndexForward= False,
        Limit= 1
    )

    # 最新レコードDeisable化
    print('Disable latest ngrok record..')
    res['Items'][0]['STATUS'] = 'Disable'
    table.put_item(
        Item= res['Items'][0]
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

    with open(f'cache/{text}_{speaker}_{emotion}_{emlv}_{pitch}_{speed}_{volume}.wav', 'wb')as f:
        f.write(vt.to_wave(text))
        cast(f"{ngrokurl}/cache/{text}_{speaker}_{emotion}_{emlv}_{pitch}_{speed}_{volume}.wav", "audio/wav")
    return

def cast(url, mimetype):
    print(f"wav URL is {url}.")
    mc = device.media_controller
    mc.play_media(url, mimetype)
    mc.block_until_active()
    return


app = Flask(__name__)
app.config['port'] = 8080


@app.route("/")
def index():
    return("hello flask")


@app.route("/cache/<string:path>")
def send_chache(path):
    # print(path)
    return send_from_directory("cache", path)


@app.route("/makeNotify", methods=['POST'])
def hoge():
    data = request.data.decode('utf-8')
    # print('data',data)
    jdata = json.loads(data)
    print('jdata', jdata)
    message = jdata['text']

    speakers = ['show', 'haruka', 'hikari', 'takeru', 'santa', 'bear']
    emotions = ['happiness', 'anger', 'sadness']

    speaker = speakers[1]
    emotion = emotions[0]
    emlv = 2
    pitch = 100
    speed = 100
    volume = 120

    if 'id' in jdata:
        speaker = speakers[jdata['id']]
    if 'em' in jdata:
        emotion = emotions[jdata['em']]
    if 'emlv' in jdata:
        emlv = jdata['emlv']
    if 'p' in jdata:
        pitch = jdata['p']
    if 's' in jdata:
        speed = jdata['s']
    if 'v' in jdata:
        volume = jdata['v']
    # print(jd['text'])

    print('message', message)
    print('speaker', speaker)
    print('emotion', emotion)
    print('emlv', emlv)
    print('pitch', pitch)
    print('speed', speed)
    print('volume', volume)

    make_wav(message, speaker, emotion, emlv, pitch, speed, volume)

    return {
        'statusCode': 200,
        'body': json.dumps('send message')
    }


# main script
u = get_ngrok_addr()
update_ngrok_url(u)
app.run()
