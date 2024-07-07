from dotenv import dotenv_values, set_key
from pathlib import Path
from os.path import exists


CONFIG = dotenv_values()
DIRNAME = Path(__file__).parent.parent
IMG_FOLDER = Path(DIRNAME, "imgs")

_env_file = Path(DIRNAME, ".env")
if not exists(_env_file):
    _env_file.touch(mode=0o600, exist_ok=False)

try:
    WU_KEY = CONFIG["WU_KEY"]
    assert WU_KEY
except (KeyError, AssertionError):
    # log
    print("\nWeather Underground API key not found...\n")
    WU_KEY = input("    Enter Weather Underground API Key: ").strip()
    set_key(_env_file, "WU_KEY", WU_KEY)

try:
    WU_STATIONS = [i for i in CONFIG["WU_STATIONS"].split(",") if i]
    assert WU_STATIONS
except (KeyError, AssertionError):
    # log
    print("\nWeather Underground station ID(s) not found...\n")
    WU_STATIONS = []
    cont = True
    while cont:
        WU_STATIONS.append(input("    Enter Station ID: ").strip())
        cont = input("      Add another (y/n)? ").lower() == "y"
    set_key(_env_file, "WU_STATIONS", ",".join(WU_STATIONS))

try:
    FORECAST_ZIPCODE = CONFIG["FORECAST_ZIPCODE"]
    assert FORECAST_ZIPCODE
except (KeyError, AssertionError):
    # log
    print("\nForecast Zipcode not found...\n")
    FORECAST_ZIPCODE = input("    Enter Forecast Zipcode: ").strip()
    set_key(_env_file, "FORECAST_ZIPCODE", FORECAST_ZIPCODE)

try:
    from inky.auto import auto

    inky_display = auto()

    DISPLAY_BLACK = inky_display.BLACK
    DISPLAY_WHITE = inky_display.WHITE
    DISPLAY_YELLOW = inky_display.YELLOW
    DISPLAY_WIDTH = inky_display.WIDTH
    DISPLAY_HEIGHT = inky_display.HEIGHT
except ImportError:
    # Log error
    DISPLAY_BLACK = (0, 0, 0)
    DISPLAY_WHITE = (255, 255, 255)
    DISPLAY_YELLOW = (255, 255, 0)
    DISPLAY_WIDTH = 250
    DISPLAY_HEIGHT = 122
