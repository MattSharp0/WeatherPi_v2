# WeatherPi v2

A simple weather display for Inky pHat e-ink display

Built on Python3.10, may not work on earlier versions

`~ python3.10 WeatherPi_v2 -h` to see optional args.

---

To use on your own raspberry pi w/ Inky pHat display:

1. Clone repository on to rasberry pi (or run locally to see a PNG version)
2. Install requirements `pip install requirements.txt`
3. In same directory, create a python file (config.py) with a dictionary with the following items filled in:

   1. Zipcode: a US zipcode for weather forecasts
   2. ApiKey: a valid, weather underground API key ([sign up here](https://www.wunderground.com/signup))
   3. Stations: 1 or more local Weather Underground weather station IDs stored in a nexted dictionary, these IDs can be found by looking at a local WU forecast and clicking on an individual station to get its ID. Ex: KDEN or KCODENVE131

   Sample dictionary: `WU_CREDENTIALS = {'ZIPCODE': '','APIKEY': '', 'STATIONS': {0: '', 1: ''}}`

4. Run the program!
   - With no flags, the program will display the current conditions and summarise the forecast
   - With flag `-I` or `--Image` it will show an image
   - With flag `-T *sample text*` or `--Text *sample text*` it will display text.

ToDos:

- ~~Add weather symbols bottom right~~
- ~~Utilise yellow color on display~~
- ~~Remove extra narative after 3pm~~
- Update images to display with correct colours
- ~~decrease font size at certain narative string length~~
- ~~decrease font size at certain short narative string length~~
- Specify exception on line 165
- Find better font?
