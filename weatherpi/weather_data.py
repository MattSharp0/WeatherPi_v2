import requests
import json


class DataError(Exception):
    def __init__(self, m, *args):
        super().__init__(args)
        self.m = m

    def __str__(self):
        return f"DataError: {self.m}"


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


def get_data(credentials: dict) -> dict:
    """
    Gets weather from weather.com api
    Returns combined dict of conditions and forecast data
    """

    url = "https://api.weather.com/v2/pws/observations/current"

    params = {
        "stationId": credentials["STATIONS"][0],
        "format": "json",
        "units": "e",
        "apiKey": credentials["APIKEY"],
    }

    response = requests.get(url, params)

    # check respose has data
    if response.status_code != 200:
        TryAltStation = True
    else:
        TryAltStation = False

    # check alternate stations
    n = 0
    while TryAltStation:
        params["stationId"] = credentials["STATIONS"][n]
        response = requests.get(url, params)
        if response.status_code == 200:
            TryAltStation = False
        elif n + 1 == len(credentials["STATIONS"]):
            raise DataError("Stations Returned No Data")
        else:
            n += 1

    weather_data = json.loads(response.text)

    raw_conditions = {
        "Temp": weather_data["observations"][0]["imperial"]["temp"],
        "Windchill": weather_data["observations"][0]["imperial"]["windChill"],
        "HeatIndex": weather_data["observations"][0]["imperial"]["heatIndex"],
        "Time": weather_data["observations"][0]["obsTimeLocal"],
        "Humidity": weather_data["observations"][0]["humidity"],
    }

    current_temp = _feels_like(
        raw_conditions["Temp"], raw_conditions["HeatIndex"], raw_conditions["Windchill"]
    )

    # Get just hour:min:sec
    w_time = (raw_conditions["Time"]).split(" ")[-1]

    # Get forcast
    forecast_url = f"https://api.weather.com/v3/wx/forecast/daily/5day?postalKey={credentials['ZIPCODE']}:US&units=e&language=en-US&format=json&apiKey={credentials['APIKEY']}"

    response = requests.get(forecast_url)

    if response.status_code != 200:
        raise DataError("Forcast Request Failed")

    weather_data = json.loads(response.text)

    forecast = {
        "Daypart_1": {
            "Part": weather_data["daypart"][0]["daypartName"][0],
            "Temp": weather_data["daypart"][0]["temperature"][0],
            "HeatIndex": weather_data["daypart"][0]["temperatureHeatIndex"][0],
            "WindChill": weather_data["daypart"][0]["temperatureWindChill"][0],
            "Narative": weather_data["daypart"][0]["narrative"][0],
            "phrase": weather_data["daypart"][0]["wxPhraseShort"][0],
            "iconCode": weather_data["daypart"][0]["iconCode"][0],
        },
        "Daypart_2": {
            "Part": weather_data["daypart"][0]["daypartName"][1],
            "Temp": weather_data["daypart"][0]["temperature"][1],
            "HeatIndex": weather_data["daypart"][0]["temperatureHeatIndex"][1],
            "WindChill": weather_data["daypart"][0]["temperatureWindChill"][1],
            "Narative": weather_data["daypart"][0]["narrative"][1],
            "phrase": weather_data["daypart"][0]["wxPhraseShort"][1],
            "iconCode": weather_data["daypart"][0]["iconCode"][1],
        },
    }

    # Degrees F symbol
    degf = "\N{DEGREE SIGN}" + "F"

    # If daypart 1 values are blank, use daypart 2 data for outlook.
    if forecast["Daypart_1"]["Temp"] == None:
        fl_temp = _feels_like(
            forecast["Daypart_2"]["Temp"],
            forecast["Daypart_2"]["HeatIndex"],
            forecast["Daypart_2"]["WindChill"],
        )
        narative = forecast["Daypart_2"]["Narative"]
        outlook = f"{forecast['Daypart_2']['Part']}: {fl_temp}{degf} | {forecast['Daypart_2']['phrase']}"
        iconcode = forecast["Daypart_2"]["iconCode"]
    else:
        fl_temp = _feels_like(
            forecast["Daypart_1"]["Temp"],
            forecast["Daypart_1"]["HeatIndex"],
            forecast["Daypart_1"]["WindChill"],
        )
        narative = forecast["Daypart_1"]["Narative"]
        outlook = f"{forecast['Daypart_1']['Part']}: {fl_temp}{degf} | {forecast['Daypart_1']['phrase']}"
        iconcode = forecast["Daypart_1"]["iconCode"]

    conditions = {
        "Temp": f"Feels like {current_temp}{degf}",
        "Humidity": f'Humidity: {raw_conditions["Humidity"]}%',
        "Narative": narative,
        "Outlook": outlook,
        "iconCode": iconcode,
        "Time": w_time,
    }

    return conditions
