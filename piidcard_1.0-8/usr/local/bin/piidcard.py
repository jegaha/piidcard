import time
import subprocess
import signal

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

disp.fill(0)
disp.show()

width = disp.width
height = disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)

padding = -2
top = padding
x = 0

fontSize = 14
#font = ImageFont.load_default()
font = ImageFont.truetype('/usr/share/fonts/truetype/arkpandora/AerialMonoBd.ttf', fontSize)

def drawClear():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    return

def drawBar(value: float, min: float, max: float):
    range = max - min
    percent = value-min * 100 / range
    draw.rectangle((x, height/2, width-1, height-1), outline=1, fill=0)
    draw.rectangle((x, height/2, width * percent / 100, height-1), outline=1, fill=1)

def drawHostIP():
    cmd = "hostname"
    Host = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    draw.text((x, top + 0), Host , font=font, fill=255)
    draw.text((x, top + 16), IP, font=font, fill=255)
    return

def drawCPU():
    cmd = "top -bn1 | grep load | awk '{printf \"%.2f %.2f %.2f\", $(NF-2), $(NF-1),$(NF-0)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    draw.text((x, top + 0), "CPU Load:", font=font, fill=255)
    draw.text((x, top + 16), CPU, font=font, fill=255)
    return

def drawMem():
    cmd = "free -m | awk 'NR==2{printf \"%s/%s\", $3,$2 }'"
    memUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    memValues = memUsage.split("/")
    percent = float(memValues[0]) * 100 / float(memValues[1])
    draw.text((x, top), "Mem: " + memValues[0] + "/" + memValues[1] + "MB", font=font, fill=255)
    drawBar(percent, 0, 100)
    return

def drawHDD():
    cmd = 'df -h | awk \'$NF=="/"{printf "%.1f/%d/%d", $3,$2,$5}\''
    disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
    diskValues = disk.split("/")
    use = float(diskValues[0])
    total = float(diskValues[1])
    percent = int(diskValues[2])
    draw.text((x, top), "HDD: " + str(use) + "/" + str(total), font=font, fill=255)
    drawBar(percent, 0, 100)
    return

def show():
    disp.image(image.rotate(180))
    disp.show()
    return

def cardHostIP():
    drawClear()
    drawHostIP()
    show()
    return

def cardCPU():
    drawClear()
    drawCPU();
    show()

def cardMem():
    drawClear()
    drawMem()
    show()
    return

def cardHDD():
    drawClear()
    drawHDD()
    show()
    return

def cardShutdown():
    drawClear()
    draw.text((x+20, top+8 ), "Shutdown...", font=font, fill=255)
    show()
    time.sleep(0.2)
    return

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

def calculateCardIndexByTime(cards, duration: int):
    amountOfCards = len(cards)
    timestamp = int(time.time())
    index = int(timestamp / duration) % amountOfCards
    return index

if __name__ == '__main__':
    killer = GracefulKiller()
    cardIndex = -1;

    cards = [cardHostIP, cardCPU, cardMem, cardHDD]
    duration = 4;

    while not killer.kill_now:
        cardIndex = calculateCardIndexByTime(cards, duration)
        cards[cardIndex]()
        time.sleep(0.2)

    cardShutdown()
