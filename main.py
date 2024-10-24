from datetime import datetime
from PIL import Image
from weatherpi.draw_functions import draw_image, draw_text, draw_weather
from weatherpi.exceptions import DataError
from weatherpi.log import get_logger, clear_logs
from weatherpi.weather_data import generate_weather_data
from weatherpi.setup import DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_WHITE

import argparse

parser = argparse.ArgumentParser(
    description="WeatherPi_V3 - Displays weather at current locations. Use -h to see optional args & additional functionality"
)
options = parser.add_mutually_exclusive_group()
options.add_argument("-I", "--Image", help="Display image", action="store_true")
options.add_argument("-T", "--Text", help="Display text, ex. -T <text to display>")
args = parser.parse_args()

log = get_logger(__name__)


def main():
    log.info("Weatherpi startup")

    current_time = datetime.now()
    if current_time.hour == 1 and current_time.minute < 30:
        log.info("Clearing outdated logs")
        clear_logs()

    img = Image.new(mode="P", size=(DISPLAY_WIDTH, DISPLAY_HEIGHT), color=DISPLAY_WHITE)

    if args.Image:
        log.debug("Draw image called")
        img = draw_image()
    elif args.Text:
        log.debug(f"Draw text called with text: {str(args.Text)}")
        draw_text(img, text=str(args.Text))
    else:
        log.debug("Draw weather called")
        try:
            weater_data = generate_weather_data()
            draw_weather(img, weather_data=weater_data)
        except DataError as de:
            log.error(f"Error occured during Draw Weather. Error: {de}")
            draw_text(img, str(de))

    try:
        from weatherpi.setup import inky_display

        log.debug("Inky Display import successful")
        inky_display.set_image(img)
        inky_display.show()
        log.info("Script executed successfully")
    except ImportError:
        log.debug("Inky Display import failure")
        img.show()
    finally:
        img.close()


if __name__ == "__main__":
    main()
