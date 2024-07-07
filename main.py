from PIL import Image
from weatherpi.weather_data import get_data, DataError
from weatherpi.draw_functions import draw_image, draw_text, draw_weather
from weatherpi.setup import DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_WHITE

import argparse

parser = argparse.ArgumentParser(
    description="WeatherPi_V3 - Displays weather at current locations. Use -h to see optional args & additional functionality"
)
options = parser.add_mutually_exclusive_group()
options.add_argument("-I", "--Image", help="Display image", action="")
options.add_argument("-T", "--Text", help="Display text, ex. -T <text to display>")
args = parser.parse_args()


def main():
    img = Image.new(mode="P", size=(DISPLAY_WIDTH, DISPLAY_HEIGHT), color=DISPLAY_WHITE)

    if args.Image:
        img = draw_image(img_name=str(args.Image))
    elif args.Text:
        draw_text(img, text=str(args.Text))
    else:
        try:
            weater_data = get_data()
            draw_weather(img, weather_data=weater_data)
        except DataError as de:
            draw_text(img, str(de))

    try:
        from weatherpi.setup import inky_display

        inky_display.set_image(img)
        inky_display.show()
    except:
        img.show()
    img.close()


if __name__ == "__main__":
    main()
