# API doc

## API Path

|path| 概要| parameter|
|:---|:---|:---------|
|/makeNotify| googleHomeにしゃべらせる| |
|/makeRecord| homeDBにデータ追加| [must] request_type, body{}|

## request_type

|name| pattern|
|:---|:---|
|intent_osewa_detail| data={who, category, detail}. 裏で自動付与. type=record, subtype=osewa, datetime=now, place=null, |
|intent_search_osewa| data={when, who, category}|
