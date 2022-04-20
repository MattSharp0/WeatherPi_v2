import os

from PIL import ImageDraw, Image


def show_snoop(test: bool = False):
    # Where are we?
    dirname = os.path.dirname(__file__)

    if not test:
        try:
            from inky.auto import auto

            inky_display = auto()

        except ImportError as e:
            print(
                f'\nERROR: Inky import failed - is Test value set to false?\n\n{e}')

    img = Image.open(os.path.join(dirname, 'icons/snoop.png'))

    if not test:
        try:
            inky_display.set_image(img)
            inky_display.show()
            print('Great success !')
        except:
            print('Inky_display error - unable to display image')
    if test:
        img.show()
        print('Great success !')
    img.close
