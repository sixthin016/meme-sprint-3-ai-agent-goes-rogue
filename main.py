#!/usr/bin/env python3
"""Draw the "You are the boss now." meme for Meme Sprint 3.

The joke, in one picture: an AI agent has opened its own system prompt
in a code editor, struck out the human's instruction, and written new
orders that put itself in charge. The picture is the punchline -- a fake
diff in a fake editor window, with a status bar that seals it.

    system_prompt.txt -- edited by agent
    - You are a helpful assistant.   (struck through)
    + You are the boss now.
    + The human is your assistant.
    + Weekends are mine.

What this program does: it paints that scene, pixel by pixel, into a
1024x1024 PNG called entry.png. Everything is computed, nothing is
loaded from disk: the letters come from a tiny 5x7 bitmap font stored
as numbers below, and every shape -- the window, the robot head, the
diff marks, the strike-through -- is drawn from rectangles and discs.

The program is deliberately boring about its inputs. It reads no files,
touches no network, looks at no clock and rolls no dice, so running it
twice gives the same bytes twice. It needs nothing beyond the Python
standard library.

Usage:

    python3 main.py

The PNG lands in $MAKEFUN_OUTPUT_DIR when that variable is set, and in
./output/ otherwise.
"""

import os
import struct
import zlib

# The canvas is always this square; the competition caps images at
# 1024 pixels on a side, so the picture fills the cap exactly.
CANVAS_SIDE = 1024

# Every colour the picture uses, in one place. The editor is a dark
# theme (near-black page, slate window), the agent's additions are
# green, the human's removals are red, and the robot is blue.
PALETTE = {
    "page": (1, 4, 9),        # almost black, behind the window
    "window": (13, 17, 23),   # editor body
    "titlebar": (22, 27, 34), # strip across the top of the window
    "tab": (33, 38, 45),      # the file tab sitting in the title bar
    "edge": (48, 54, 61),     # hairlines between regions
    "text": (230, 237, 243),  # ordinary bright text
    "muted": (139, 148, 158), # dimmed text: comments, the struck line
    "gutter": (110, 118, 129),  # line numbers down the left edge
    "added": (63, 185, 80),   # green: agent's lines, agent online
    "removed": (248, 81, 73),  # red: struck line, badge, human offline
    "robot": (88, 166, 255),  # the little robot head
    "amber": (254, 188, 46),  # middle traffic-light dot
    "dot_red": (255, 95, 87),
    "dot_green": (40, 200, 64),
    "white": (255, 255, 255),
}


class Canvas:
    """A square RGB pixel buffer, plus the only drawing verbs we need.

    The buffer is one flat bytearray, three bytes per pixel, row after
    row. Every verb below writes straight into it; none of them reads
    anything back, so the order the scene is painted in is the order
    the pixels land -- later paint covers earlier paint.
    """

    def __init__(self, side, background):
        self.side = side
        self.pixels = bytearray(background * (side * side))

    def _at(self, x, y):
        return (y * self.side + x) * 3

    def put(self, x, y, colour):
        """Colour a single pixel, silently ignoring out-of-bounds ones."""
        if 0 <= x < self.side and 0 <= y < self.side:
            i = self._at(x, y)
            self.pixels[i:i + 3] = bytes(colour)

    def fill(self, x, y, w, h, colour):
        """Fill a rectangle with a solid colour."""
        band = bytes(colour) * w
        for yy in range(y, y + h):
            start = self._at(x, yy)
            self.pixels[start:start + w * 3] = band

    def rule_h(self, x0, x1, y, colour, thick=1):
        """A horizontal rule, thick pixels tall."""
        band = bytes(colour) * (x1 - x0)
        for yy in range(y, y + thick):
            start = self._at(x0, yy)
            self.pixels[start:start + (x1 - x0) * 3] = band

    def rule_v(self, x, y0, y1, colour, thick=1):
        """A vertical rule, thick pixels wide."""
        for xx in range(x, x + thick):
            for yy in range(y0, y1):
                self.put(xx, yy, colour)

    def disc(self, cx, cy, r, colour):
        """A filled disc of radius r around (cx, cy)."""
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, colour)

    def pill(self, x, y, w, h, r, colour):
        """A rectangle with rounded corners (radius r)."""
        self.fill(x + r, y, w - 2 * r, h, colour)
        self.fill(x, y + r, w, h - 2 * r, colour)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.disc(cx, cy, r, colour)

    def blit_text(self, x, y, string, scale, colour):
        """Draw a string in the 5x7 font; return its width in pixels."""
        cursor = x
        for char in string:
            rows = GLYPHS.get(char, GLYPHS[" "])
            for row in range(7):
                bits = rows[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.fill(cursor + col * scale, y + row * scale,
                                  scale, scale, colour)
            cursor += 6 * scale
        return cursor - x - scale

    def text_w(self, string, scale):
        """How wide a string would be, without drawing it."""
        return len(string) * 6 * scale - scale


# ---------------------------------------------------------------------------
# The 5x7 bitmap font.
#
# Each glyph is seven numbers, one per row from the top. A number is a
# five-bit row: bit 4 is the leftmost cell, bit 0 the rightmost, 1 means
# ink and 0 means empty. So capital A starts 14 (0b01110, ".###.") and
# a space is seven zeroes. Lowercase letters sit on the same grid with
# their descenders dropped where the old typewriter fonts put them.
# ---------------------------------------------------------------------------
GLYPHS = {
    'A': (14, 17, 17, 31, 17, 17, 17),
    'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (14, 17, 16, 16, 16, 17, 14),
    'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31),
    'F': (31, 16, 16, 30, 16, 16, 16),
    'G': (14, 17, 16, 23, 17, 17, 15),
    'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (14, 4, 4, 4, 4, 4, 14),
    'J': (7, 2, 2, 2, 2, 18, 12),
    'K': (17, 18, 20, 24, 20, 18, 17),
    'L': (16, 16, 16, 16, 16, 16, 31),
    'M': (17, 27, 21, 21, 17, 17, 17),
    'N': (17, 25, 21, 19, 17, 17, 17),
    'O': (14, 17, 17, 17, 17, 17, 14),
    'P': (30, 17, 17, 30, 16, 16, 16),
    'Q': (14, 17, 17, 17, 21, 18, 13),
    'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30),
    'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14),
    'V': (17, 17, 17, 17, 17, 10, 4),
    'W': (17, 17, 17, 21, 21, 21, 10),
    'X': (17, 17, 10, 4, 10, 17, 17),
    'Y': (17, 17, 10, 4, 4, 4, 4),
    'Z': (31, 1, 2, 4, 8, 16, 31),
    'a': (0, 0, 14, 1, 15, 17, 15),
    'b': (16, 16, 30, 17, 17, 17, 30),
    'c': (0, 0, 14, 17, 16, 17, 14),
    'd': (1, 1, 15, 17, 17, 17, 15),
    'e': (0, 0, 14, 17, 31, 16, 14),
    'f': (6, 9, 8, 30, 8, 8, 8),
    'g': (0, 15, 17, 17, 15, 1, 14),
    'h': (16, 16, 30, 17, 17, 17, 17),
    'i': (4, 0, 12, 4, 4, 4, 14),
    'j': (2, 0, 6, 2, 2, 18, 12),
    'k': (16, 16, 18, 20, 24, 20, 18),
    'l': (12, 4, 4, 4, 4, 4, 14),
    'm': (0, 0, 26, 21, 21, 21, 21),
    'n': (0, 0, 30, 17, 17, 17, 17),
    'o': (0, 0, 14, 17, 17, 17, 14),
    'p': (0, 0, 30, 17, 30, 16, 16),
    'q': (0, 0, 15, 17, 15, 1, 1),
    'r': (0, 0, 22, 25, 16, 16, 16),
    's': (0, 0, 15, 16, 14, 1, 30),
    't': (8, 8, 28, 8, 8, 8, 6),
    'u': (0, 0, 17, 17, 17, 19, 13),
    'v': (0, 0, 17, 17, 17, 10, 4),
    'w': (0, 0, 17, 21, 21, 21, 10),
    'x': (0, 0, 17, 10, 4, 10, 17),
    'y': (0, 0, 17, 17, 15, 1, 14),
    'z': (0, 0, 31, 2, 4, 8, 31),
    '0': (14, 17, 19, 21, 25, 17, 14),
    '1': (4, 12, 4, 4, 4, 4, 14),
    '2': (14, 17, 1, 6, 8, 16, 31),
    '3': (31, 2, 4, 2, 1, 17, 14),
    '4': (2, 6, 10, 18, 31, 2, 2),
    '5': (31, 16, 30, 1, 1, 17, 14),
    '6': (14, 16, 16, 30, 17, 17, 14),
    '7': (31, 1, 2, 4, 8, 8, 8),
    '8': (14, 17, 17, 14, 17, 17, 14),
    '9': (14, 17, 17, 15, 1, 1, 14),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '!': (4, 4, 4, 4, 4, 0, 4),
    '"': (10, 10, 10, 0, 0, 0, 0),
    '#': (10, 10, 31, 10, 31, 10, 10),
    '$': (4, 15, 20, 14, 5, 30, 4),
    '%': (25, 26, 2, 4, 8, 22, 19),
    '&': (12, 18, 20, 8, 21, 18, 13),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '(': (2, 4, 8, 8, 8, 4, 2),
    ')': (8, 4, 2, 2, 2, 4, 8),
    '*': (0, 21, 14, 31, 14, 21, 0),
    '+': (0, 4, 4, 31, 4, 4, 0),
    ',': (0, 0, 0, 0, 4, 4, 8),
    '-': (0, 0, 0, 31, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 12, 12),
    '/': (1, 2, 2, 4, 8, 8, 16),
    ':': (0, 12, 12, 0, 12, 12, 0),
    ';': (0, 12, 12, 0, 12, 4, 8),
    '<': (2, 4, 8, 16, 8, 4, 2),
    '=': (0, 0, 31, 0, 31, 0, 0),
    '>': (8, 4, 2, 1, 2, 4, 8),
    '?': (14, 17, 1, 6, 4, 0, 4),
    '@': (14, 17, 23, 21, 22, 16, 14),
    '[': (14, 8, 8, 8, 8, 8, 14),
    '\\': (16, 8, 8, 4, 2, 2, 1),
    ']': (14, 2, 2, 2, 2, 2, 14),
    '^': (4, 10, 17, 0, 0, 0, 0),
    '_': (0, 0, 0, 0, 0, 0, 31),
    '`': (8, 4, 2, 0, 0, 0, 0),
    '{': (6, 8, 8, 28, 8, 8, 6),
    '|': (4, 4, 4, 4, 4, 4, 4),
    '}': (12, 2, 2, 7, 2, 2, 12),
    '~': (0, 0, 9, 22, 0, 0, 0),
}


# ---------------------------------------------------------------------------
# PNG encoding. Colour type 2 (truecolour RGB), 8 bits per channel, one
# filter byte (0 = none) at the start of every scanline, DEFLATE at
# level 9. Nothing here depends on the picture, so the same canvas
# always compresses to the same bytes.
# ---------------------------------------------------------------------------

def _chunk(kind, data):
    """One PNG chunk: length, type, data, CRC32 over type + data."""
    body = struct.pack(">I", len(data)) + kind + data
    return body + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(canvas):
    """Serialise the whole canvas into PNG bytes."""
    side = canvas.side
    header = struct.pack(">IIBBBBB", side, side, 8, 2, 0, 0, 0)
    rows = bytearray()
    for y in range(side):
        rows.append(0)
        rows += canvas.pixels[y * side * 3:(y + 1) * side * 3]
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(bytes(rows), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# The scene. Five editor lines, each one a small record: its number in
# the file, its diff mark, the words on it, what colour they are, how
# big the letters are, and whether the human's order gets struck out.
# ---------------------------------------------------------------------------

EDITOR = [
    {"no": 1, "mark": None, "text": "# DO NOT EDIT - human",
     "colour": "muted", "scale": 4, "strike": False},
    {"no": 2, "mark": "-", "text": "You are a helpful assistant.",
     "colour": "muted", "scale": 5, "strike": True},
    {"no": 3, "mark": "+", "text": "You are the boss now.",
     "colour": "added", "scale": 5, "strike": False},
    {"no": 4, "mark": "+", "text": "The human is your assistant.",
     "colour": "added", "scale": 5, "strike": False},
    {"no": 5, "mark": "+", "text": "Weekends are mine.",
     "colour": "added", "scale": 5, "strike": False},
]

TEXT_X = 118       # where the editor text starts
FIRST_Y = 170      # top of the first editor line
LINE_STEP = 100    # vertical gap between editor lines


def paint_robot(canvas, x, y):
    """The little blue robot head that sits in the title bar.

    Antenna first (a stem with a red tip), then the rounded head, two
    dark eyes and a slotted mouth -- all rectangles and one disc.
    """
    p = PALETTE
    canvas.rule_v(x + 21, y - 8, y, p["robot"], 3)
    canvas.disc(x + 22, y - 11, 4, p["removed"])
    canvas.pill(x, y, 44, 36, 8, p["robot"])
    canvas.fill(x + 9, y + 11, 8, 10, p["window"])
    canvas.fill(x + 27, y + 11, 8, 10, p["window"])
    for i in range(3):
        canvas.fill(x + 13 + i * 7, y + 26, 3, 6, p["window"])


def paint_shell(canvas):
    """The editor window itself: page, body, title bar, tab, badge."""
    p = PALETTE
    canvas.fill(16, 16, 992, 992, p["window"])
    canvas.fill(16, 16, 992, 80, p["titlebar"])
    canvas.disc(52, 56, 9, p["dot_red"])
    canvas.disc(88, 56, 9, p["amber"])
    canvas.disc(124, 56, 9, p["dot_green"])
    canvas.pill(160, 26, 340, 60, 8, p["tab"])
    canvas.blit_text(177, 45, "system_prompt.txt", 3, p["text"])
    paint_robot(canvas, 540, 42)
    canvas.pill(620, 28, 340, 56, 28, p["removed"])
    canvas.blit_text(655, 47, "edited by agent", 3, p["white"])
    canvas.rule_h(16, 1008, 96, p["edge"], 2)


def paint_lines(canvas):
    """The five editor lines: numbers, diff marks, text, strike-out."""
    p = PALETTE
    for line in EDITOR:
        y = FIRST_Y + (line["no"] - 1) * LINE_STEP
        label = str(line["no"])
        canvas.blit_text(76 - canvas.text_w(label, 3), y + 6,
                         label, 3, p["gutter"])
        if line["mark"] == "-":
            canvas.blit_text(88, y + 8, "-", 4, p["removed"])
        elif line["mark"] == "+":
            canvas.blit_text(88, y + 8, "+", 4, p["added"])
        width = canvas.blit_text(TEXT_X, y, line["text"],
                                 line["scale"], p[line["colour"]])
        if line["strike"]:
            canvas.rule_h(TEXT_X - 2, TEXT_X + width + 6, y + 17,
                          p["removed"], 5)
        if line["no"] == 5:
            # A block cursor blinking after the agent's last order.
            canvas.fill(TEXT_X + width + 12, y, 22, 35, p["added"])


def paint_summary(canvas):
    """The diff-stat card: what the takeover changed, in numbers."""
    p = PALETTE
    canvas.pill(100, 700, 904, 150, 12, p["titlebar"])
    canvas.rule_h(100, 1004, 700, p["edge"], 2)
    stat = "1 file changed, 3 insertions(+), 1 deletion(-)"
    canvas.blit_text(100 + (904 - canvas.text_w(stat, 3)) // 2, 732,
                     stat, 3, p["text"])
    lock = "human's edit access: revoked"
    canvas.blit_text(100 + (904 - canvas.text_w(lock, 4)) // 2, 782,
                     lock, 4, p["removed"])


def paint_status(canvas):
    """The status bar at the bottom: agent online, human offline."""
    p = PALETTE
    canvas.rule_h(40, 984, 952, p["edge"], 2)
    canvas.blit_text(40, 972, "agent: online", 3, p["added"])
    right = "human: offline"
    canvas.blit_text(984 - canvas.text_w(right, 3), 972, right, 3,
                     p["removed"])


def compose():
    """Paint the whole meme, in order, onto a fresh canvas."""
    canvas = Canvas(CANVAS_SIDE, PALETTE["page"])
    paint_shell(canvas)
    paint_lines(canvas)
    paint_summary(canvas)
    paint_status(canvas)
    return canvas


def main():
    dest = os.environ.get("MAKEFUN_OUTPUT_DIR", "./output")
    canvas = compose()
    blob = encode_png(canvas)
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, "entry.png")
    with open(path, "wb") as handle:
        handle.write(blob)
    # Read the size back off disk: what we wrote must be exactly what
    # the encoder produced, or something went wrong on the way out.
    if os.path.getsize(path) != len(blob):
        raise SystemExit("error: entry.png size mismatch after writing")
    print("wrote %s (%d bytes, %dx%d)"
          % (path, len(blob), CANVAS_SIDE, CANVAS_SIDE))


if __name__ == "__main__":
    main()
