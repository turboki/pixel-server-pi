import time
import re
import neopixel
import board
import tornado.ioloop
import tornado.web
import signal
import pixel_utils
import multiprocessing
from multiprocessing.managers import BaseManager

class MyManager(BaseManager): pass

def Manager():
    m = MyManager()
    m.start()
    return m

class PixelConfig(object):
    def __init__(self):
        self._running = True
        self._done = False
        self._mode = 'rainbow'
        self._colors = [(255,0,0)]
        self._wait_time = 0.001
        self._brightness = 0.2
        self._steps = None

    def get_steps(self):
        return self._steps

    def set_steps(self, steps):
        self._steps = steps

    def get_done(self):
        return self._done

    def set_done(self, done):
        self._done = done

    def get_running(self):
        return self._running

    def set_running(self, running):
        self._running = running

    def get_mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = mode

    def get_colors(self):
        return self._colors

    def set_colors(self, colors):
        self._colors = colors

    def get_wait_time(self):
        return self._wait_time

    def set_wait_time(self, wait_time):
        self._wait_time = wait_time

    def get_brightness(self):
        return self._brightness

    def set_brightness(self, brightness):
        self._brightness = brightness

def increment_loop(curr, max):
    if curr < max:
        return curr + 1
    else:
        return 0

COLOR_NAMES = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred ': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgrey': '#d3d3d3',
    'lightgreen': '#90ee90',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370d8',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#d87093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'rebeccapurple': '#663399',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}

def get_colors(color_param):
    if color_param == '':
        return []
    color_arr =  color_param.split(',')
    return list(filter(lambda s: s != '', map(get_color, color_arr)))

def get_color(color_string):
    if color_string in COLOR_NAMES:
        return hex_to_rgb(COLOR_NAMES.get(color_string)[1:])
    match = re.match(r'#([0-9a-f]{6})', color_string)
    if match:
        return hex_to_rgb(color_string[1:])
    return ''

def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def parse_steps(steps = None):
    if steps == None or steps == "":
        return []
    return list(filter(lambda s: s != None, map(parse_step, steps.split('|'))))

def parse_step(step = ''):
    step_components = step.split(':')
    if len(step_components) != 4:
        print ('Invalid Step: %s' % step)
        return None
    return {
        'mode': step_components[0],
        'colors': get_colors(step_components[1]),
        'wait': float(step_components[2]),
        'loop': float(step_components[3])
    }

def led_loop(led_config_proxy, thread_id):
    pixels = neopixel.NeoPixel(board.D18, 450, brightness=0.2, auto_write=False, pixel_order=neopixel.RGB)
    pixels.fill((255,255,255))
    pixels.show()
    heartbeat = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    creepy = [0.1, 0.2, 0.1, 0.2, 0.3, 0, 0.1, 0.5, 0.4, 0.2, 0.1, 0.3, 0.1, 0.3, 0.1, 0.3, 0.9, 1, 0.9, 0.1, 1, 0.3, 0.1, 0.2, 0.3, 0, 0.1, 0.5]

    _current_mode = 'rainbow'
    _current_colors = [(0,0,0)]
    _current_brightness = 0.2
    _current_steps = None
    _current_steps_list = []
    _current_loop = 0
    _current_step = 0

    _twinkle_colors = []
    _twinkle_alphas = []
    _current_rgb_index = 0
    _current_pixel_index = 0
    _current_colors_index = 0
    _current_alpha = (0,True)
    while True:
        done = led_config_proxy.get_done()
        running = led_config_proxy.get_running()
        brightness = led_config_proxy.get_brightness()
        if (done):
            break
        steps = led_config_proxy.get_steps()
        if steps != _current_steps:
            _current_steps = steps
            _current_steps_list = parse_steps(steps)
            _current_loop = 0
            _current_step = 0

        if _current_steps == None:

            mode = led_config_proxy.get_mode()
            colors = led_config_proxy.get_colors()
            wait_time = led_config_proxy.get_wait_time()

        else:
            loop = _current_steps_list[_current_step]['loop']
            if _current_loop >= loop:
                _current_step = increment_loop(_current_step, len(_current_steps_list)-1)
                _current_loop = 0
            mode = _current_steps_list[_current_step]['mode']
            colors = _current_steps_list[_current_step]['colors']
            wait_time = _current_steps_list[_current_step]['wait']

        if  mode != _current_mode or colors != _current_colors:
            _current_mode = mode
            _current_colors = colors

            _strip_colors = []
            _strip_alphas = []
            _current_rgb_index = 0
            _current_pixel_index = 0
            _current_colors_index = 0
            _current_alpha = (0, True)

        if _current_brightness != brightness:
            _current_brightness = brightness
            pixels.brightness = _current_brightness
        if running == True:
            if _current_mode == 'rainbow':
                pixel_utils.rainbow(pixels,_current_rgb_index),
                _current_rgb_index = increment_loop(_current_rgb_index, 255)
                if _current_rgb_index == 0:
                    _current_loop += 1
            elif mode == 'solid_rainbow':
                pixel_utils.solid_rainbow(pixels, _current_rgb_index),
                _current_rgb_index = increment_loop(_current_rgb_index, 255)
                if _current_rgb_index == 0:
                    _current_loop += 1
            elif mode == 'solid' and len(colors) > 0:
                pixels.fill(colors[_current_colors_index])
                pixels.show()
                _current_colors_index = increment_loop(_current_colors_index, len(colors)-1)
                if _current_colors_index == 0:
                    _current_loop += 1
            elif mode == 'fade' and len(colors) > 0:
                c = colors[_current_colors_index]
                f = (round(c[0] * _current_alpha[0]), round(c[1] * _current_alpha[0]), round(c[2] * _current_alpha[0]))
                pixels.fill(f)
                pixels.show()
                _current_alpha = pixel_utils.alpha_increment(_current_alpha[0], _current_alpha[1])
                if (_current_alpha[0] == 0):
                    _current_colors_index = increment_loop(_current_colors_index, len(colors)-1)
                    if _current_colors_index == 0:
                        _current_loop += 1
            elif mode == "chase":
                if (len(colors) > 0):
                    pixel_utils.color_chase(pixels, _current_pixel_index, colors[_current_colors_index])
                    _current_pixel_index = increment_loop(_current_pixel_index, len(pixels)-1)
                    if _current_pixel_index == 0:
                        _current_colors_index = increment_loop(_current_colors_index, len(colors)-1)
                        if  _current_colors_index == 0:
                            _current_loop += 1
            elif mode == "twinkle":
                if len(_strip_colors) == 0:
                    t = pixel_utils.twinkle_init(pixels, colors)
                    _strip_colors = t[0]
                pixel_utils.twinkle(pixels, _strip_colors)
                _current_pixel_index = increment_loop(_current_pixel_index, len(pixels)-1)
                if _current_pixel_index == 0:
                    _current_loop += 1
            elif mode == "twinkle_adv":
                if len(_strip_colors) == 0:
                    t = pixel_utils.twinkle_init(pixels, colors)
                    _strip_colors = t[0]
                    _strip_alphas = t[1]
                pixel_utils.twinkle_adv(pixels, _strip_colors, _strip_alphas)
                _strip_alphas = pixel_utils.twinkle_alpha_increment(_strip_alphas)
                _current_pixel_index = increment_loop(_current_pixel_index, len(pixels)-1)
                if _current_pixel_index == 0:
                    _current_loop += 1
            elif mode == "marquee":
                if len(_strip_colors) == 0:
                    _strip_colors = pixel_utils.marquee_init(pixels, colors)
                pixel_utils.marquee(pixels, _strip_colors)
                _current_pixel_index = increment_loop(_current_pixel_index, len(pixels)-1)
                if _current_pixel_index == 0:
                    _current_loop += 1
            elif mode == "wave":
                print()
            elif mode == 'heartbeat' and len(colors) > 0:
                c = colors[_current_colors_index]
                f = (round(c[0] * heartbeat[_current_pixel_index]), round(c[1] * heartbeat[_current_pixel_index]), round(c[2] * heartbeat[_current_pixel_index]))
                pixels.fill(f)
                pixels.show()
                _current_pixel_index = increment_loop(_current_pixel_index, len(heartbeat)-1)
                if (_current_pixel_index == 0):
                    _current_colors_index = increment_loop(_current_colors_index, len(colors)-1)
                    if _current_colors_index == 0:
                        _current_loop += 1
            elif mode == 'creepy' and len(colors) > 0:
                c = colors[_current_colors_index]
                f = (round(c[0] * creepy[_current_pixel_index]), round(c[1] * creepy[_current_pixel_index]), round(c[2] * creepy[_current_pixel_index]))
                pixels.fill(f)
                pixels.show()
                _current_pixel_index = increment_loop(_current_pixel_index, len(creepy)-1)
                if (_current_pixel_index == 0):
                    _current_colors_index = increment_loop(_current_colors_index, len(colors)-1)
                    if _current_colors_index == 0:
                        _current_loop += 1
            else:
                pixel_utils.off(pixels)
            time.sleep(wait_time)
        else:
            pixel_utils.off(pixels)
            time.sleep(1)

    pixel_utils.off(pixels)
    return led_config_proxy


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class ModeController(tornado.web.RequestHandler):
    def initialize(self, pixel_config):
        self.pixel_config = pixel_config

    def get(self):
        running = self.get_argument('running', 'true', True)
        mode = self.get_argument('mode', None, True)
        wait = self.get_argument('wait', None, True)
        colors = self.get_argument('colors',None, True)
        brightness = self.get_argument('brightness',None, True)
        steps = self.get_argument('steps',None, True)
        self.pixel_config.set_steps(steps)
        mutations = {}
        if running == 'false':
            self.pixel_config.set_running(False)
            mutations['running'] = False
        elif running == 'true':
            self.pixel_config.set_running(True)
            mutations['running'] = True
        if mode != None:
            mutations['mode'] = mode
            self.pixel_config.set_mode(mode)
        if colors != None:
            rgb_colors = get_colors(colors)
            mutations['colors'] = rgb_colors
            self.pixel_config.set_colors(rgb_colors)
        if wait != None:
            try:
                mutations['wait'] = float(wait)
                self.pixel_config.set_wait_time(float(wait))
            except:
                pass
        if brightness != None:
            try:
                mutations['brightness'] = float(brightness)
                self.pixel_config.set_brightness(float(brightness))
            except:
                pass
        self.finish(mutations)


if __name__ == '__main__':
    print('Starting Manager');
    MyManager.register('PixelConfig', PixelConfig)
    manager = Manager()
    pixel_config = manager.PixelConfig()
    p = multiprocessing.Process(target=led_loop, args=(pixel_config, 'Pixel Loop'))
    app = tornado.web.Application([\
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "/var/www/pixel/static/"}),
        (r'/api', ModeController, {'pixel_config' : pixel_config}),\
        (r'/', MainHandler, {})\
    ])
    app.listen(80)
    loop = tornado.ioloop.IOLoop.current()
    try:
        print('Starting LED Loop');
        p.start()
        print('Starting Web Server');
        loop.start()

    except KeyboardInterrupt:
        print('Exiting')
        pass
    finally:
        print('Finally')
        pixel_config.set_done(True)
        print('Stopping Web Server');
        loop.stop()       # might be redundant, the loop has already stopped
        loop.close(True)  # needed to close all open sockets
        print('Stopping LED Loop');
        p.join()
        print('Stopping Manager');
        manager.shutdown()