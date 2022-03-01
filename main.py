from pprint import pprint
import requests
import json
import os


from PIL import ImageFont, ImageDraw, Image

from config import WU_CREDENTIALS

# Where are we?
dirname = os.path.dirname(__file__)


def feels_like(temp: int, heatindex: int, windchill: int) -> int:
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


def insert_newlines(sentence: str, line_len: int = 40) -> str:
    '''
    Insert new lines into str if over a certain length
    '''

    for x in range(line_len, 0, -1):
        if sentence[x] == ' ':
            pos = x + 1
            break

    return '\n'.join(sentence[i:i+pos] for i in range(0, len(sentence), pos))


def get_weather_data() -> dict:
    '''
    Get and formats weather data, returns dict with three variables:
    Current Temp, Daypart 1 conditions and Daypart 2 condtions.
    '''

    # Get current temp:
    conditions_url = f"https://api.weather.com/v2/pws/observations/current?stationId={WU_CREDENTIALS['STATION']}&format=json&units=e&apiKey={WU_CREDENTIALS['APIKEY']}"

    response = requests.get(conditions_url)

    weather_data = json.loads(response.text)

    conditions = {'Temp': weather_data['observations'][0]['imperial']['temp'],
                  'Windchill': weather_data['observations'][0]['imperial']['windChill'],
                  'HeatIndex': weather_data['observations'][0]['imperial']['heatIndex'],
                  'Time': weather_data['observations'][0]['obsTimeLocal']
                  }

    current_temp = feels_like(
        conditions['Temp'], conditions['HeatIndex'], conditions['Windchill'])

    w_time = (conditions['Time']).split(' ')[-1]

    # Get forcast

    forecast_url = f"https://api.weather.com/v3/wx/forecast/daily/5day?postalKey={WU_CREDENTIALS['ZIPCODE']}:US&units=e&language=en-US&format=json&apiKey={WU_CREDENTIALS['APIKEY']}"

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

    # If daypart 1 values are Null, copy daypart 2 data.
    if forecast['Daypart_1']['Temp'] == None:
        for x in forecast['Daypart_1']:
            forecast['Daypart_1'][x] = forecast['Daypart_2'][x]

    # Determine feels like temperatures
    daypart_1_temp = feels_like(
        forecast['Daypart_1']['Temp'], forecast['Daypart_1']['HeatIndex'], forecast['Daypart_1']['WindChill'])
    daypart_2_temp = feels_like(
        forecast['Daypart_2']['Temp'], forecast['Daypart_2']['HeatIndex'], forecast['Daypart_2']['WindChill'])

    # Degrees F symbol
    degf = u'\N{DEGREE SIGN}' + 'F'

    conditions = {
        'Temp': f'Feels like {current_temp}{degf}',
        'Daypart_1': f"{forecast['Daypart_1']['Part']}: {daypart_1_temp}{degf} | {forecast['Daypart_1']['phrase']}",
        'Daypart_2': f"{forecast['Daypart_2']['Part']}: {daypart_2_temp}{degf} | {forecast['Daypart_2']['phrase']}",
        'Narative': forecast['Daypart_1']['Narative'],
        'iconCode': forecast['Daypart_1']['iconCode'],
        'Time': w_time
    }

    return conditions


def display_conditions(condtions: dict, test: bool = False) -> None:
    '''
    Display conditions locally (using test = True) or on an inky phat display
    '''

    if not test:
        try:
            from inky.auto import auto

            inky_display = auto()

            black = inky_display.BLACK
            white = inky_display.WHITE
            yellow = inky_display.YELLOW
            width = inky_display.WIDTH
            height = inky_display.HEIGHT

        except ImportError as e:
            print(
                f'\nERROR: Inky import failed - is Test value set to false?\n\n{e}')

    # allows for testing without inky library
    if test:
        pprint(conditions)
        # define colors and inky display size
        black = (0, 0, 0)
        white = (255, 255, 255)
        yellow = (255, 255, 0)
        width, height = 250, 122

    # Create image
    img = Image.new(mode='P', size=(width, height), color=(white))
    draw = ImageDraw.Draw(im=img)

    # load icon image
    icon = Image.open(os.path.join(
        dirname, f"icons/{(str(conditions['iconCode']) + '.png')}"))
    # icon = Image.open('Test_icons/38.png')

    img.paste(icon, (190, 70))
    icon.close

    # Define font
    font_lg = ImageFont.truetype(os.path.join(
        dirname, 'fonts/MerriweatherSans-Medium.ttf'), size=24)
    font_md = ImageFont.truetype(os.path.join(
        dirname, 'fonts/MerriweatherSans-Medium.ttf'), size=14)
    font_sm = ImageFont.truetype(os.path.join(
        dirname, 'fonts/MerriweatherSans-Regular.ttf'), size=12)
    font_xsm = ImageFont.truetype(os.path.join(
        dirname, 'fonts/RobotoMono-Regular.ttf'), size=8)

    w, _ = font_sm.getsize(conditions['Narative'])

    if w > 240:
        conditions['Narative'] = insert_newlines(conditions['Narative'])
        ny = 35
    else:
        ny = 40

    w, _ = font_lg.getsize(conditions['Temp'])

    # Draw data
    draw.text(xy=(5, 4), text=condtions['Temp'], fill=black, font=font_lg)
    draw.text(xy=(205, 4), text=conditions['Time'], fill=black, font=font_xsm)
    draw.line(xy=((0, 32), ((w+5), 32)), fill=yellow, width=2)
    draw.text(xy=(5, ny), text=condtions['Narative'], fill=black, font=font_sm)
    draw.text(
        xy=(5, 85), text=condtions['Daypart_1'], fill=black, font=font_md)
    draw.text(
        xy=(5, 100), text=condtions['Daypart_2'], fill=black, font=font_md)

    if not test:
        try:
            inky_display.set_image(img)
            inky_display.show()
            print('Great success !')
        except:
            print('Inky_display error - unable to display image')
    if test:
        img.show()


conditions = get_weather_data()

img = display_conditions(conditions, test=True)
