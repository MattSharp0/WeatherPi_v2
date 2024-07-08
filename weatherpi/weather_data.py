from weatherpi.setup import WU_KEY, WU_STATIONS, FORECAST_ZIPCODE
from weatherpi.exceptions import DataError
import requests

DEG_F = "\N{DEGREE SIGN}" + "F"


def _feels_like(temp: int, heatindex: int, windchill: int) -> int:
    """
    Determines which temperature is most accurate based on WU logic:
    Use windchill if temp below 61, heatindex if above 70
    """
    if temp < 61:
        feels_like_temp = windchill
    elif temp > 70:
        feels_like_temp = heatindex
    else:
        feels_like_temp = temp

    return feels_like_temp


def get_current_conditions():
    url = "https://api.weather.com/v2/pws/observations/current"

    params = {
        "stationId": "",
        "format": "json",
        "units": "e",
        "apiKey": WU_KEY,
    }

    active_station = False
    i = 0
    while not active_station and i <= len(WU_STATIONS) - 1:
        params["stationId"] = WU_STATIONS[i]
        raw_conditions = requests.get(url, params)
        active_station = raw_conditions.status_code == 200
        # Log station used and success
        i += 1
    if not active_station and i == len(WU_STATIONS):
        raise DataError(f"Invalid conditions response code: {raw_conditions.status_code}")

    try:
        conditions_data = raw_conditions.json()
    except requests.JSONDecodeError as e:
        raise DataError(f"Could not decode conditions JSON: {e}")

    conditions = {
        "Temp": conditions_data["observations"][0]["imperial"]["temp"],
        "Windchill": conditions_data["observations"][0]["imperial"]["windChill"],
        "HeatIndex": conditions_data["observations"][0]["imperial"]["heatIndex"],
        "Time": conditions_data["observations"][0]["obsTimeLocal"].split(" ")[-1],
        "Humidity": conditions_data["observations"][0]["humidity"],
        "UVIndex": conditions_data["observations"][0]["uv"],
    }

    conditions["FeelsLikeTemp"] = _feels_like(conditions["Temp"], conditions["HeatIndex"], conditions["Windchill"])

    return conditions


def get_forecast():

    url = "https://api.weather.com/v3/wx/forecast/daily/5day"

    params = {
        "postalKey": FORECAST_ZIPCODE + ":US",
        "units": "e",
        "language": "en-US",
        "format": "json",
        "apiKey": WU_KEY,
    }

    raw_forecast = requests.get(url, params)

    try:
        assert raw_forecast.status_code == 200
    except AssertionError:
        raise DataError(f"Invalid forecast response code: {raw_forecast.status_code}")

    try:
        forecast_data = raw_forecast.json()
    except requests.JSONDecodeError as e:
        raise DataError(f"Could not decode forecast JSON: {e}")

    if forecast_data["daypart"][0]["temperature"][0]:
        daypart = 0
    else:
        daypart = 1
    # Log daypart used

    return {
        "Part": forecast_data["daypart"][0]["daypartName"][daypart],
        "Temp": forecast_data["daypart"][0]["temperature"][daypart],
        "HeatIndex": forecast_data["daypart"][0]["temperatureHeatIndex"][daypart],
        "WindChill": forecast_data["daypart"][0]["temperatureWindChill"][daypart],
        "ForecastFeelsLikeTemp": _feels_like(
            forecast_data["daypart"][0]["temperature"][daypart],
            forecast_data["daypart"][0]["temperatureHeatIndex"][daypart],
            forecast_data["daypart"][0]["temperatureWindChill"][daypart],
        ),
        "Narative": forecast_data["daypart"][0]["narrative"][daypart],
        "PhraseLong": forecast_data["daypart"][0]["wxPhraseLong"][daypart],
        "PhraseShort": forecast_data["daypart"][0]["wxPhraseShort"][daypart],
        "QualifierPhrase": forecast_data["daypart"][0]["qualifierPhrase"][daypart],
        "IconCode": forecast_data["daypart"][0]["iconCode"][daypart],
    }


def generate_weather_data():

    forecast_data = get_forecast()

    conditions_data = get_current_conditions()

    if forecast_data["QualifierPhrase"]:
        narative = f"{forecast_data['PhraseLong']}, {forecast_data['QualifierPhrase']}"
    else:
        narative = f"{forecast_data['PhraseLong']}"

    return {
        "Temp": f"Feels like {conditions_data['FeelsLikeTemp']}{DEG_F}",
        "Humidity": f"Humidity: {conditions_data['Humidity']}%",
        "Narative": narative,
        "Outlook": f"{forecast_data['Part']}: {forecast_data['ForecastFeelsLikeTemp']} {DEG_F} | {forecast_data['PhraseShort']}",
        "UV Index": f"UV Index: {conditions_data['UVIndex']}",
        "IconCode": forecast_data["IconCode"],
        "Time": conditions_data["Time"],
    }
