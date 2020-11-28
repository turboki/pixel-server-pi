#!/usr/bin/python3
# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel
import threading
import re
import random
import web


# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 450
running = True
done = False
mode = "rainbow"
colors = [(0,0,0)]
brightness = 0.2
wait_time = 0.001

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.RGB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=brightness, auto_write=False, pixel_order=ORDER)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rainbow(index, wait):
    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels) + index
        pixels[i] = wheel(pixel_index & 255)
    pixels.show()
    time.sleep(wait)

def solid_rainbow(index, wait):
    pixels.fill(wheel(index & 255))
    pixels.show()
    time.sleep(wait)

def marquee_init():
    __marquee_colors = []
    __segment_size = num_pixels // len(colors)
    for i in range(num_pixels):
        __color_index = (i // __segment_size) % len(colors)
        __marquee_colors.append(colors[__color_index])
    return __marquee_colors

def marquee(colors, wait):
    for i in range(num_pixels):
        pixels[i] = colors[i]
    pixels.show()
    time.sleep(wait)
    colors.insert(0, colors.pop())


def twinkle_init():
    __twinkle_colors = []
    __twinkle_alphas = []
    for i in range(num_pixels):
        __twinkle_colors.append(random.choice(colors))
        __twinkle_alphas.append((random.random(), random.choice([True, False])))
    return (__twinkle_colors, __twinkle_alphas)

def twinkle(twinkle_colors, wait):
    for i in range(num_pixels):
        _current_alpha = random.random()
        _current_color = twinkle_colors[i]
        pixels[i] = (round (_current_color[0] * _current_alpha), round(_current_color[1] * _current_alpha), round(_current_color[2] * _current_alpha))
    pixels.show()
    time.sleep(wait)

def twinkle_adv(twinkle_colors, twinkle_alphas, wait):
    for i in range(num_pixels):
        _current_color = twinkle_colors[i]
        _current_alpha = twinkle_alphas[i][0]
        pixels[i] = (round (_current_color[0] * _current_alpha), round(_current_color[1] * _current_alpha), round(_current_color[2] * _current_alpha))
    pixels.show()
    time.sleep(wait)

def twinkle_alpha_increment(alphas):
    new_alphas = []
    for i in range(len(alphas)):
        __current_alpha = alphas[i][0]
        __current_direction_up = alphas[i][1]
        if __current_direction_up:
            if __current_alpha >= 0.95:
                new_alphas.append((1, False))
            else:
                new_alphas.append((__current_alpha + 0.05, True))
        else:
            if __current_alpha <= 0.05:
                new_alphas.append((0, True))
            else:
                new_alphas.append((__current_alpha - 0.05, False))
    return new_alphas

def color_chase(index, color, wait):
    pixels[index] = color
    pixels.show()
    time.sleep(wait)

def off():
    pixels.fill((0,0,0))
    pixels.show()

def increment_loop(curr, max):
    if curr < max:
        return curr + 1
    else:
        return 0


def led_loop():
    _current_mode = "rainbow"
    _current_colors = [(0,0,0)]
    _current_brightness = 0.2

    _twinkle_colors = []
    _twinkle_alphas = []
    _current_rgb_index = 0
    _current_pixel_index = 0
    _current_colors_index = 0
    while True:
        if mode != _current_mode or colors != _current_colors:
            _current_mode = mode
            _current_colors = colors

            _strip_colors = []
            _strip_alphas = []
            _current_rgb_index = 0
            _current_pixel_index = 0
            _current_colors_index = 0

        if _current_brightness != brightness:
            _current_brightness = brightness
            pixels.brightness = _current_brightness

        if done == True:
            off()
            break
        if running == True:
            if mode == "rainbow":
                rainbow(_current_rgb_index,wait_time),
                _current_rgb_index = increment_loop(_current_rgb_index, 255)
            elif mode == "solid_rainbow":
                solid_rainbow(_current_rgb_index,wait_time),
                _current_rgb_index = increment_loop(_current_rgb_index, 255)
            elif mode == "solid":
                pixels.fill(colors[_current_colors_index])
                pixels.show()
                _current_colors_index = increment_loop(_current_colors_index, len(colors)-1)
                time.sleep(wait_time)
            elif mode == "chase":
                color_chase(_current_pixel_index, colors[_current_colors_index], wait_time)
                _current_pixel_index = increment_loop(_current_pixel_index, num_pixels-1)
                if _current_pixel_index == 0:
                    _current_colors_index = increment_loop(_current_colors_index, len(colors)-1)
            elif mode == "twinkle":
                if len(_strip_colors) == 0:
                    t = twinkle_init()
                    _strip_colors = t[0]
                twinkle(_strip_colors, wait_time)
            elif mode == "twinkle_adv":
                if len(_strip_colors) == 0:
                    t = twinkle_init()
                    _strip_colors = t[0]
                    _strip_alphas = t[1]
                twinkle_adv(_strip_colors, _strip_alphas, wait_time)
                _strip_alphas = twinkle_alpha_increment(_strip_alphas)
            elif mode == "marquee":
                if len(_strip_colors) == 0:
                    t = marquee_init()
                    _strip_colors = marquee_init()
                marquee(_strip_colors, wait_time)
            elif mode == "wave":
                print()
            else:
                off()
        else:
            off()

class ledThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
   def run(self):
      threadLock.acquire()
      led_loop()
      threadLock.release()

class MyWebserver(threading.Thread):

    def run (self):
        urls = ('/', 'MyWebserver')
        app = web.application(urls, globals())
        app.run()

    def GET(self):
        off()
        return "Hello, world!"

threadLock = threading.Lock()

led_thread = ledThread(1, "LED Loop")
led_thread.start()
#web_thread = MyWebserver()
#web_thread.start()

try:

    while True:
        m = input("\nMode: ")
        if m == "off":
            running = False
        elif m == "on":
            running = True
        elif m == "exit":
            running = False
            done = True
            break;
        elif m == "debug":
            for i in range(num_pixels):
                print(pixels[i])
        else:
            match = re.match(r'(rainbow|solid_rainbow) (\d+(\.\d+)?)', m)
            if match:
                off()
                running = True
                mode = match.group(1)
                wait_time = float(match.group(2))

            match = re.match(r'(solid|chase|twinkle|twinkle_adv|marquee|wave) (\d+(\.\d+)?) #(([0-9a-f]{6}))', m)
            if match:
                off()
                running = True
                mode = match.group(1)
                wait_time = float(match.group(2))
                matches = re.findall(r'#([0-9a-f]{6})', m)
                colors = list(map(hex_to_rgb, matches))
            match = re.match(r'(bright) ((?!0*[.]0*$|[.]0*$|0*$)\d+[.]?\d{0,2})', m)
            if match:
                newBrightness = float(match.group(2))
                if newBrightness > 1:
                    newBrightness = 1
                brightness = newBrightness
    off()
    led_thread.join()
 #   web_thread.join()
except KeyboardInterrupt:
    running = False
    done = True
    led_thread.join()
 #   web_thread.join()
    off()
