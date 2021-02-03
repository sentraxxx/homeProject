# OpenWeather API

## url

[API Doc](https://home.openweathermap.org/)

## limit
Hourly forecast: unavailable  
Daily forecast: unavailable  
Calls per minute: 60  
3 hour forecast: 5 days  


## How to make an API call
API call:
> https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&
exclude={part}&appid={YOUR API KEY}

**lat, lon** geographical coordinates (latitude, longitude)  
**API key** unique API key (you can always find it on the account page, on the "API key" tab)  
**part** (optional parameter) by using this parameter you can exclude some parts of weather data from the API response. The value parts should be a comma-delimited list (without spaces). Available values:

current  
minutely  
hourly  
daily  



