import random

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
    return (r, g, b)

def rainbow(pixels, index):
    num_pixels = len(pixels)
    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels) + index
        pixels[i] = wheel(pixel_index & 255)
    pixels.show()

def solid_rainbow(pixels, index):
    pixels.fill(wheel(index & 255))
    pixels.show()

def marquee_init(pixels, colors = []):
    __marquee_colors = []
    __segment_size = len(pixels) // len(colors)
    for i in range(len(pixels)):
        __color_index = (i // __segment_size) % len(colors)
        __marquee_colors.append(colors[__color_index])
    return __marquee_colors

def marquee(pixels, colors):
    for i in range(len(pixels)):
        pixels[i] = colors[i]
    pixels.show()
    colors.insert(0, colors.pop())


def twinkle_init(pixels, colors):
    __twinkle_colors = []
    __twinkle_alphas = []
    for i in range(len(pixels)):
        __twinkle_colors.append(random.choice(colors))
        __twinkle_alphas.append((random.random(), random.choice([True, False])))
    return (__twinkle_colors, __twinkle_alphas)

def twinkle(pixels, twinkle_colors):
    for i in range(len(pixels)):
        _current_alpha = random.random()
        _current_color = twinkle_colors[i]
        pixels[i] = (round (_current_color[0] * _current_alpha), round(_current_color[1] * _current_alpha), round(_current_color[2] * _current_alpha))
    pixels.show()

def twinkle_adv(pixels, twinkle_colors, twinkle_alphas):
    for i in range(len(pixels)):
        _current_color = twinkle_colors[i]
        _current_alpha = twinkle_alphas[i][0]
        pixels[i] = (round (_current_color[0] * _current_alpha), round(_current_color[1] * _current_alpha), round(_current_color[2] * _current_alpha))
    pixels.show()

def twinkle_alpha_increment(alphas):
    new_alphas = []
    for i in range(len(alphas)):
        __current_alpha = alphas[i][0]
        __current_direction_up = alphas[i][1]
        new_alphas.append(alpha_increment(__current_alpha, __current_direction_up))
    return new_alphas

def alpha_increment(alpha, up):
    new_alpha = (0, True)
    if up:
        if alpha >= 0.95:
            new_alpha = (1, False)
        else:
            new_alpha = (alpha + 0.05, True)
    else:
        if alpha <= 0.05:
            new_alpha = (0, True)
        else:
            new_alpha = (alpha - 0.05, False)
    return new_alpha

def color_chase(pixels, index, color):
    pixels[index] = color
    pixels.show()

def off(pixels):
    pixels.fill((0,0,0))
    pixels.show()