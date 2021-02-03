# event DB schema

## type

|name| 用途|
|:---|:---|
|alarm| 時刻指定で発動するアラーム. 処理後は 'alarm_done'に変更する. |
|alarm_done| 処理済みのアラーム |
|condition| 現在の状態に使用. subtype='current...'に使用. subtype毎に最大1つ.|
|record| 過去の記録. |

## subtype

|name| device| 用途|
|:---|:---|:---|
| cpu_temp           |vcgencmd| RaspberryPiのCPU温度記録 |
| current_cpu_temp   |vcgencmd| RaspberryPiのCPU温度 |
| current_home_temp  |natureRemo| 現在の室温 |
| current_rain_level |YahooAPI| 現在の降水量 |
| current_temp       |OpenWeatherAPI| 現在の外気温 |
| current_weather    |OpenWeatherAPI| 現在の天気 |
| google_home_notify |N/A | google homeにしゃべらせるアラーム |
| home_temp          |natureRemo| 室温の記録 |
| rain_level         |YahooAPI| 降水量の記録、予報 |
| temp               |OpenWeatherAPI| 外気温の記録 |
| weather            |OpenWeatherAPI| 天気の記録 |
| osewa              |入力デバイス| おしっこ、うんち記録 |

## data

|subtype             |datetime |place     |param|
|:-------------------|:--------|:---------|:--------------|
| cpu_temp           |測定時刻  | 計測地点 | cpu_temp: CPU温度
| current_cpu_temp   |最終更新時刻| 計測地点 | cpu_temp: CPU温度
| current_home_temp  |最終更新時刻| 計測地点 | temp: 室温
| current_rain_level |最終更新時刻| 計測地点 | RainFall: 降水量
| current_temp       |最終更新時刻| 計測地点 |　temp: 外気温
| current_weather    |最終更新時刻| 計測地点 | OpenWeatherAPI結果参照
| google_home_notify |トリガ発動時刻| N/A | status: enable(未処理), disable(処理済み)<br>text: しゃべらせるテキスト<br>last_update: 処理時刻
| home_temp          |測定時刻| 計測地点 | temp: 室温
| rain_level         |予報時刻| 計測地点 | observacion: 現在降水量<br>forecast[]:予想降水量
| temp               |測定時刻| 計測地点 | temp: 外気温
| weather            |測定時刻| 計測地点 | OpenWeatherAPI結果参照
| osewa             |記録時刻| N/A | who: 対象<br>categoly: 分類<br>detail: free_strings

## OpenWeatherAPI sample

{"dt": 1594286405, "sunrise": 1594236781, "sunset": 1594288764, "temp": 23.62, "feels_like": 23.25, "pressure": 1010, "humidity": 94, "dew_point": 22.6, "uvi": 11.65, "clouds": 75, "visibility": 10000, "wind_speed": 7.7, "wind_deg": 200, "weather": [{"id": 501, "main": "Rain", "description": "u9069u5ea6u306au96e8", "icon": "10d"}], "rain": {"1h": 1.78}, "date": "202007091820"
