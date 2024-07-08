from PIL import ImageFont, ImageDraw, Image
from os.path import join
from weatherpi.setup import (
    DIRNAME,
    DISPLAY_BLACK,
    DISPLAY_WHITE,
    DISPLAY_YELLOW,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    IMG_FOLDER,
)

import textwrap


# define fonts
font_lg = ImageFont.truetype(join(DIRNAME, "fonts/MerriweatherSans-Medium.ttf"), size=24)
font_md = ImageFont.truetype(join(DIRNAME, "fonts/MerriweatherSans-Medium.ttf"), size=14)
font_sm = ImageFont.truetype(join(DIRNAME, "fonts/MerriweatherSans-Regular.ttf"), size=12)
font_xsm = ImageFont.truetype(join(DIRNAME, "fonts/MerriweatherSans-Regular.ttf"), size=10)
font_xxsm = ImageFont.truetype(join(DIRNAME, "fonts/RobotoMono-Regular.ttf"), size=8)


def draw_weather(base_image: Image, weather_data: dict) -> object:

    draw = ImageDraw.Draw(im=base_image)

    # Draw weather icon
    with Image.open(join(DIRNAME, "icons", str(weather_data["IconCode"]) + ".png")) as icon:
        base_image.paste(icon, (190, 70))

    # Draw/write weather info
    draw.text(xy=(5, 4), text=weather_data["Temp"], fill=DISPLAY_BLACK, font=font_lg)  # Feels like

    draw.text(xy=(205, 4), text=weather_data["Time"], fill=DISPLAY_BLACK, font=font_xxsm)  # Time stamp

    draw.line(
        xy=((0, 32), ((font_lg.getlength(weather_data["Temp"]) + 5), 32)), fill=DISPLAY_YELLOW, width=2
    )  # Underline feels like text

    if font_sm.getlength(weather_data["Narative"]) > 240:
        weather_data["Narative"] = "\n".join(textwrap.wrap(weather_data["Narative"], 40))
        nar_font = font_xsm
        ny = 35
    else:
        ny = 40
        nar_font = font_sm
    draw.text(xy=(5, ny), text=weather_data["Narative"], fill=DISPLAY_BLACK, font=nar_font)

    if len(weather_data["Outlook"]) > 25:
        cond_font = font_sm
    else:
        cond_font = font_md

    draw.text(xy=(5, 70), text=weather_data["UV Index"], fill=DISPLAY_BLACK, font=font_sm)
    draw.text(xy=(5, 85), text=weather_data["Humidity"], fill=DISPLAY_BLACK, font=font_sm)

    draw.text(xy=(5, 100), text=weather_data["Outlook"], fill=DISPLAY_BLACK, font=cond_font)

    return base_image


def draw_text(base_image: object, text: str) -> object:
    draw = ImageDraw.Draw(im=base_image)

    text = "\n".join(textwrap.wrap(text, 20))

    draw.text(
        xy=(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2),
        text=text,
        fill=DISPLAY_BLACK,
        font=font_md,
        align="center",
        anchor="mm",
    )

    return base_image


def draw_image(img_name: str = "snoop") -> None:
    img_name = img_name + ".png"
    return Image.open(join(DIRNAME, IMG_FOLDER, img_name))
