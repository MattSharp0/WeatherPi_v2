from PIL import ImageFont, ImageDraw, Image
from weather_data import get_conditions
from config import WU_CREDENTIALS

import os

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
    print(
        f'\nERROR: Inky import failed - default values used.\n\n{e}')


# define fonts
font_lg = ImageFont.truetype(os.path.join(
    dirname, 'fonts/MerriweatherSans-Medium.ttf'), size=24)
font_md = ImageFont.truetype(os.path.join(
    dirname, 'fonts/MerriweatherSans-Medium.ttf'), size=14)
font_sm = ImageFont.truetype(os.path.join(
    dirname, 'fonts/MerriweatherSans-Regular.ttf'), size=12)
font_xsm = ImageFont.truetype(os.path.join(
    dirname, 'fonts/MerriweatherSans-Regular.ttf'), size=10)
font_xxsm = ImageFont.truetype(os.path.join(
    dirname, 'fonts/RobotoMono-Regular.ttf'), size=8)


def insert_newlines(sentence: str, line_len: int = 40) -> str:
    '''
    Insert new lines into str if over a certain length
    '''
    for x in range(line_len, 0, -1):
        if sentence[x] == ' ':
            pos = x + 1
            break

    return '\n'.join(sentence[i:i+pos] for i in range(0, len(sentence), pos))


def draw_weather(base_image: object) -> object:

    conditions = get_conditions(credentials=WU_CREDENTIALS)

    draw = ImageDraw.Draw(im=base_image)

    # Draw weather icon
    with Image.open(os.path.join(
            dirname, f"icons/{(str(conditions['iconCode']) + '.png')}")) as icon:
        base_image.paste(icon, (190, 70))

    # Draw/write weather info
    draw.text(
        xy=(5, 4), text=conditions['Temp'], fill=black, font=font_lg)  # Feels like

    draw.text(xy=(205, 4),
              text=conditions['Time'], fill=black, font=font_xxsm)  # Time stamp

    w, _ = font_lg.getsize(conditions['Temp'])
    draw.line(xy=((0, 32), ((w+5), 32)), fill=yellow,
              width=2)  # Underline feels like text

    w, _ = font_sm.getsize(conditions['Narative'])
    if w > 240:
        conditions['Narative'] = insert_newlines(conditions['Narative'])
        nar_font = font_xsm
        ny = 35
    else:
        ny = 40
        nar_font = font_sm
    draw.text(xy=(5, ny),
              text=conditions['Narative'], fill=black, font=nar_font)  # Narative

    if len(conditions['Daypart_1']) > 25 or len(conditions['Daypart_2']) > 25:
        cond_font = font_sm
    else:
        cond_font = font_md
    draw.text(
        xy=(5, 85), text=conditions['Daypart_1'], fill=black, font=cond_font)  # Forecast 1

    draw.text(
        xy=(5, 100), text=conditions['Daypart_2'], fill=black, font=cond_font)  # Forcast 2

    return base_image


def draw_text(base_image: object, text: str) -> object:
    draw = ImageDraw.Draw(im=base_image)

    draw.text(
        xy=(width/2, height/2), text=text, fill=black, font=font_lg)

    return base_image


def draw_image() -> None:
    with Image.open(os.path.join(dirname, 'icons/snoop.png')) as meme:
        try:
            inky_display.set_image(meme)
            inky_display.show()
        except:
            meme.show()


def main(display: str = "W", text: str = ""):
    img = Image.new(mode='P', size=(width, height), color=white)

    match display:
        case "W":
            print("case match w")
            draw_weather(img)
        case "I":
            draw_image()
        case "T":
            draw_text(base_image=img, text=text)

    try:
        inky_display.set_image(img)
        inky_display.show()
    except:
        img.show()


main()
