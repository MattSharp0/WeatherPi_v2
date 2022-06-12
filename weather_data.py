import requests
import json


def _feels_like(temp: int, heatindex: int, windchill: int) -> int:
    '''
    Determines which temperature is most accurate based on WU logic:
    Use windchill if temp below 61, heatindex if above 70
    '''
    if temp < 61:
        feels_like_temp = windchill
    elif temp > 70:
        feels_like_temp = heatindex
    else:
        feels_like_temp = temp

    return feels_like_temp


def get_conditions(credentials: dict):
    '''
    Get and formats weather data, returns dict with three variables:
    Current Temp, Daypart 1 conditions and Daypart 2 condtions.
    '''

    # Get current temp:
    conditions_url = f"https://api.weather.com/v2/pws/observations/current?stationId={credentials['STATION']}&format=json&units=e&apiKey={credentials['APIKEY']}"

    response = requests.get(conditions_url)

    weather_data = json.loads(response.text)

    conditions = {'Temp': weather_data['observations'][0]['imperial']['temp'],
                  'Windchill': weather_data['observations'][0]['imperial']['windChill'],
                  'HeatIndex': weather_data['observations'][0]['imperial']['heatIndex'],
                  'Time': weather_data['observations'][0]['obsTimeLocal']
                  }

    current_temp = _feels_like(
        conditions['Temp'], conditions['HeatIndex'], conditions['Windchill'])

    # Get just hour:min:sec
    w_time = (conditions['Time']).split(' ')[-1]

    # Get forcast
    forecast_url = f"https://api.weather.com/v3/wx/forecast/daily/5day?postalKey={credentials['ZIPCODE']}:US&units=e&language=en-US&format=json&apiKey={credentials['APIKEY']}"

    response = requests.get(forecast_url)
    weather_data = json.loads(response.text)

    forecast = {
        'Daypart_1': {
            'Part': weather_data['daypart'][0]['daypartName'][0],
            'Temp': weather_data['daypart'][0]['temperature'][0],
            'HeatIndex': weather_data['daypart'][0]['temperatureHeatIndex'][0],
            'WindChill': weather_data['daypart'][0]['temperatureWindChill'][0],
            'Narative': weather_data['daypart'][0]['narrative'][0],
            'phrase': weather_data['daypart'][0]['wxPhraseShort'][0],
            'iconCode': weather_data['daypart'][0]['iconCode'][0]
        },
        'Daypart_2': {
            'Part': weather_data['daypart'][0]['daypartName'][1],
            'Temp': weather_data['daypart'][0]['temperature'][1],
            'HeatIndex': weather_data['daypart'][0]['temperatureHeatIndex'][1],
            'WindChill': weather_data['daypart'][0]['temperatureWindChill'][1],
            'Narative': weather_data['daypart'][0]['narrative'][1],
            'phrase': weather_data['daypart'][0]['wxPhraseShort'][1],
            'iconCode': weather_data['daypart'][0]['iconCode'][1]
        }
    }

    # Degrees F symbol
    degf = u'\N{DEGREE SIGN}' + 'F'

    # If daypart 1 values are Null, copy daypart 2 data.
    if forecast['Daypart_1']['Temp'] == None:
        for x in forecast['Daypart_1']:
            forecast['Daypart_1'][x] = forecast['Daypart_2'][x]
        daypart_1 = ""
    else:
        daypart_1_temp = _feels_like(
            forecast['Daypart_1']['Temp'], forecast['Daypart_1']['HeatIndex'], forecast['Daypart_1']['WindChill'])
        daypart_1 = f"{forecast['Daypart_1']['Part']}: {daypart_1_temp}{degf} | {forecast['Daypart_1']['phrase']}"

    daypart_2_temp = _feels_like(
        forecast['Daypart_2']['Temp'], forecast['Daypart_2']['HeatIndex'], forecast['Daypart_2']['WindChill'])

    conditions = {
        'Temp': f"Feels like {current_temp}{degf}",
        'Narative': forecast['Daypart_1']['Narative'],
        'Daypart_1': daypart_1,
        'Daypart_2': f"{forecast['Daypart_2']['Part']}: {daypart_2_temp}{degf} | {forecast['Daypart_2']['phrase']}",
        'iconCode': forecast['Daypart_1']['iconCode'],
        'Time': w_time
    }

    return conditions
