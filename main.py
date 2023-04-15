from PIL import ImageFont, ImageDraw, Image
from weather_data import get_data, DataError
from config import WU_CREDENTIALS

from time import localtime, strftime, time
import os
import argparse
import textwrap

# Description and parser function
parser = argparse.ArgumentParser(
    description="WeatherPi_V2 - Displays weather at current locations. Use -h to see optional args & additional functionality"
)
options = parser.add_mutually_exclusive_group()
options.add_argument("-I", "--Image", help="Display image", action="store_true")
options.add_argument("-T", "--Text", help="Display text, ex. -T <text to display>")
args = parser.parse_args()

# Where are we?
dirname = os.path.dirname(__file__)


# Define inkypHat parameters
try:
    from inky.auto import auto

    inky_display = auto()

    black = inky_display.BLACK
    white = inky_display.WHITE
    yellow = inky_display.YELLOW
    width = inky_display.WIDTH
    height = inky_display.HEIGHT

except ImportError as e:
    # InkypHat display sizes for local viewing
    black = (0, 0, 0)
    white = (255, 255, 255)
    yellow = (255, 255, 0)
    width, height = 250, 122
    print(f"\nERROR: Inky import failed - default values used.\n\n{e}")


# define fonts
font_lg = ImageFont.truetype(
    os.path.join(dirname, "fonts/MerriweatherSans-Medium.ttf"), size=24
)
font_md = ImageFont.truetype(
    os.path.join(dirname, "fonts/MerriweatherSans-Medium.ttf"), size=14
)
font_sm = ImageFont.truetype(
    os.path.join(dirname, "fonts/MerriweatherSans-Regular.ttf"), size=12
)
font_xsm = ImageFont.truetype(
    os.path.join(dirname, "fonts/MerriweatherSans-Regular.ttf"), size=10
)
font_xxsm = ImageFont.truetype(
    os.path.join(dirname, "fonts/RobotoMono-Regular.ttf"), size=8
)


def draw_weather(base_image: object) -> object:
    conditions = get_data(credentials=WU_CREDENTIALS)

    draw = ImageDraw.Draw(im=base_image)

    # Draw weather icon
    iconcode = str(conditions["iconCode"])
    if (
        strftime("%m-%d", localtime(time())) == "04-20"
        or strftime("%H:%M", localtime(time())) == "16:20"
    ):
        iconcode = "420"

    with Image.open(os.path.join(dirname, f"icons/{(iconcode + '.png')}")) as icon:
        base_image.paste(icon, (190, 70))

    # Draw/write weather info
    draw.text(
        xy=(5, 4), text=conditions["Temp"], fill=black, font=font_lg
    )  # Feels like

    draw.text(
        xy=(205, 4), text=conditions["Time"], fill=black, font=font_xxsm
    )  # Time stamp

    w, _ = font_lg.getsize(conditions["Temp"])
    draw.line(
        xy=((0, 32), ((w + 5), 32)), fill=yellow, width=2
    )  # Underline feels like text

    w, _ = font_sm.getsize(conditions["Narative"])
    if w > 240:
        conditions["Narative"] = "\n".join(textwrap.wrap(conditions["Narative"], 40))
        nar_font = font_xsm
        ny = 35
    else:
        ny = 40
        nar_font = font_sm
    draw.text(
        xy=(5, ny), text=conditions["Narative"], fill=black, font=nar_font
    )  # Narative

    if len(conditions["Outlook"]) > 25:
        cond_font = font_sm
    else:
        cond_font = font_md

    draw.text(
        xy=(5, 85), text=conditions["Humidity"], fill=black, font=font_sm
    )  # Forecast 1

    draw.text(
        xy=(5, 100), text=conditions["Outlook"], fill=black, font=cond_font
    )  # Forcast 2

    return base_image


def draw_text(base_image: object, text: str) -> object:
    draw = ImageDraw.Draw(im=base_image)

    text = "\n".join(textwrap.wrap(text, 20))

    draw.text(
        xy=(width / 2, height / 2),
        text=text,
        fill=black,
        font=font_lg,
        align="center",
        anchor="mm",
    )

    return base_image


def draw_image() -> None:
    return Image.open(os.path.join(dirname, "icons/snoop.png"))


def main():
    img = Image.new(mode="P", size=(width, height), color=white)

    if args.Image:
        img = draw_image()
    elif args.Text:
        draw_text(img, text=str(args.Text))
    else:
        try:
            draw_weather(img)
        except DataError as de:
            draw_text(img, str(de))

    try:
        inky_display.set_image(img)
        inky_display.show()
    except:
        img.show()
    img.close()


if __name__ == "__main__":
    main()
