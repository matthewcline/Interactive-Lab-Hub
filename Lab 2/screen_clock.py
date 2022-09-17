import time
import datetime
import random
from util import scale_image
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# filenames of time markers in order
time_markers = ["good_morning.jpg", "bath_time.jpg", "sun.jpg", "lunch.jpg",
                "afternoon_nap.jpg", "post_afternoon_nap.jpg", 
                "pre_walk_excitement.JPG", "walk.jpg", 
                "snack_request_before_bed.JPG", "bed.jpg"]

cur_index = 0
manual_viewing = False

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Part D
    # cmd = f"echo '{time.strftime('%m/%d/%Y %H:%M:%S')}'" 
    # TIME = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # y = top
    # draw.text((x, y), TIME, font=font, fill="#FFFFFF")

    # Part E
    if buttonB.value and not buttonA.value:  # just button A pressed
        print("prev")

        if not manual_viewing:  # start at the beginning
            cur_index = 0
            manual_viewing = True
        elif cur_index > 0:
            cur_index -= 1 
        else:
            cur_index = len(time_markers) - 1
        # Display image.
        image = Image.open(time_markers[cur_index])
        disp.image(scale_image(image, height, width))
    if buttonA.value and not buttonB.value:  # just button B pressed
        print("next")
        
        if not manual_viewing:  # start at the beginning
            cur_index = 0
            manual_viewing = True
        elif cur_index < len(time_markers) - 1:
            cur_index += 1
        else:
            cur_index = 0

        # Display image.
        image = Image.open(time_markers[cur_index])
        disp.image(scale_image(image, height, width))
    
    elif not buttonA.value and not buttonB.value:   # both pressed
        # go back to scheduled images
        manual_viewing = False

    if not manual_viewing:
        now = datetime.datetime.now()
        wake_up = now.replace(hour=8, minute=0, second=0, microsecond=0)
        bath_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
        sun = now.replace(hour=10, minute=30, second=0, microsecond=0)
        lunch = now.replace(hour=12, minute=0, second=0, microsecond=0)
        afternoon_nap = now.replace(hour=13, minute=0, second=0, microsecond=0)
        post_afternoon_nap = now.replace(hour=15, minute=0, second=0, microsecond=0)
        pre_walk_excitement = now.replace(hour=16, minute=00, second=0, microsecond=0)
        walk = now.replace(hour=16, minute=15, second=0, microsecond=0)
        snack_request_before_bed = now.replace(hour=19, minute=30, second=0, microsecond=0)
        bed_time = now.replace(hour=20, minute=0, second=0, microsecond=0)

        if wake_up < now < bath_time:
            image = Image.open("good_morning.jpg")
        elif bath_time < now < sun:
            image = Image.open("bath_time.jpg")
        elif sun < now < lunch:
            image = Image.open("sun.jpg")
        elif lunch < now < afternoon_nap:
            image = Image.open("lunch.jpg")
        elif afternoon_nap < now < post_afternoon_nap:
            image = Image.open("afternoon_nap.jpg")
        elif post_afternoon_nap < now < pre_walk_excitement:
            image = Image.open("post_afternoon_nap.jpg")
        elif pre_walk_excitement < now < walk:
            image = Image.open("pre_walk_excitement.JPG")
        elif walk < now < snack_request_before_bed:
            image = Image.open("walk.jpg")
        elif snack_request_before_bed < now < bed_time:
            image = Image.open("snack_request_before_bed.jpg")
        else: # bed time
            image = Image.open("bed.jpg")

        # Display image.
        disp.image(scale_image(image, height, width))
        time.sleep(1)
