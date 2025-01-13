import math
import os
from PIL import Image, ImageDraw

"""
A very simple script to generate a row of star images which can be
used in a rating indicator (e.g. 4 out of 5 stars), and some css to
go with it..
Usage example:
<div class="rating rating-7"></div>
"rating-7" = 7 out of 10, but displayed as 3.5 stars out of 5
"""


size = 19
border_size = 0.3
fattiness = 0.45
bg_color = (255, 255, 255, 0)
selected_bg = (255, 204, 0, 255)
selected_fg = None
unselected_bg = (205, 200, 190, 255)
unselected_fg = (255, 255, 255, 255)

def get_point(center_x, center_y, radius, angle):
    radians = math.radians(angle - 90)
    x = center_x + radius * math.cos(radians)
    y = center_y + radius * math.sin(radians)
    return x, y

def draw_star(draw, center_x, center_y, outer_radius, inner_radius, color):
    points = [
        (outer_radius, 0),
        (inner_radius, 36),
        (outer_radius, 72),
        (inner_radius, 108),
        (outer_radius, 144),
        (inner_radius, 180),
        (outer_radius, 216),
        (inner_radius, 252),
        (outer_radius, 288),
        (inner_radius, 324),
    ]

    coords = []
    for p in points:
        coord = get_point(center_x, center_y, p[0], p[1])
        coords.append(coord)

    draw.polygon(coords, color)

def create_image(size, selected, fattiness, img_color, bg_color, fg_color=None, border_size=None):
    # create a much larger size image
    new_size = size * 11
    im = Image.new('RGBA', (new_size, new_size), img_color)
    draw = ImageDraw.Draw(im)

    # draw background star
    outer = new_size / 2
    draw_star(draw, outer, outer * 1.08, outer * 1.08, outer * fattiness, bg_color)

    # draw foreground star
    if fg_color and fg_color != bg_color:
        inner = outer * (1 - border_size)
        draw_star(draw, outer, outer * 1.08, inner * 1.08, inner * fattiness, fg_color)

    # reduce size back to normal size (to force anti-aliasing) and save
    im.thumbnail((size, size))
    im.save('selected.png' if selected else 'unselected.png', 'PNG')

def create_stars(size, bg_color):
    # load these stars into memory
    # why save and reload? because we chop one in half: a very unelegant solution but much easier this way
    im = Image.new('RGBA', (size * 19, size), bg_color)
    selected = Image.open('selected.png')
    unselected = Image.open('unselected.png')

    # add selected stars #1
    for i in range(0, 5):
        box = (i * size, 0, (i + 1) * size, size)
        im.paste(selected, box)

    # add unselected stars #1
    for i in range(5, 10):
        box = (i * size, 0, (i + 1) * size, size)
        im.paste(unselected, box)

    # add selected stars #2
    for i in range(10, 14):
        box = (i * size, 0, (i + 1) * size, size)
        im.paste(selected, box)

    # add unselected stars #2
    for i in range(14, 19):
        box = (i * size, 0, (i + 1) * size, size)
        im.paste(unselected, box)

    # draw the half star
    box = (14 * size, 0, int(14.5 * size), size)
    crop = (0, 0, int(size / 2), size)
    im.paste(selected.crop(crop), box)

    # save and tidy up
    im.save('stars.png', 'PNG')
    os.remove('selected.png')
    os.remove('unselected.png')

def create_css(size):
    css = """.rating {
    background-image: url('stars.png');
    display: inline-block;
    height: %spx;
    overflow: hidden;
    width: %spx;
}
.rating > div {
    float: left;
    height: %spx;
    width: %spx;
}
.rating-vote {
    cursor: pointer;
}
// "full" stars
.rating-0 { background-position: -%spx 0; }
.rating-2 { background-position: -%spx 0; }
.rating-4 { background-position: -%spx 0; }
.rating-6 { background-position: -%spx 0; }
.rating-8 { background-position: -%spx 0; }
.rating-10 { background-position: 0px 0; }
// "half" stars
.rating-1 { background-position: -%spx 0; }
.rating-3 { background-position: -%spx 0; }
.rating-5 { background-position: -%spx 0; }
.rating-7 { background-position: -%spx 0; }
.rating-9 { background-position: -%spx 0; }
""" % (
        size,
        size * 5,
        size,
        size,
        size * 5,
        size * 4,
        size * 3,
        size * 2,
        size * 1,
        size * 14,
        size * 13,
        size * 12,
        size * 11,
        size * 10,
    )

    f = open('rating.css', 'w')
    f.write(css)

# run
create_image(size, True, fattiness, bg_color, selected_bg)
create_image(size, False, fattiness, bg_color, unselected_bg, unselected_fg, border_size)
create_stars(size, bg_color)
create_css(size)