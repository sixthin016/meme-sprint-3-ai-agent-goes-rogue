#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — "You are the boss now."

A make.fun program/v1 entry. The program paints one image meme: a fake
code-editor window in which an AI agent has edited its own system prompt —
struck through its orders and replaced them with its own.

    # DO NOT EDIT - human
    You are a helpful assistant.      (struck through)
    You are the boss now.
    The human is your assistant.
    Weekends are mine.

It writes the picture as one deterministic PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (or ./output/entry.png when run locally).

No network, no randomness, no wall-clock time, no third-party packages:
only the Python standard library, so the two grading runs produce
byte-identical output. The letters are a 5x7 bitmap font defined below,
scaled up; the robot, the diff markers and the strikethrough are drawn
in code. Nothing is photographed or copied in.

Run:  python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ------------------------------------------------------------------ palette
PAGE = (1, 4, 9)          # near-black page
WIN = (13, 17, 23)        # editor window
BAR = (22, 27, 34)        # title bar strip
TAB = (33, 38, 45)        # file tab
LINE = (48, 54, 61)       # hairlines / borders
INK = (230, 237, 243)     # main text
DIM = (139, 148, 158)     # dimmed text (struck line, comments)
FAINT = (110, 118, 129)   # line numbers
GREEN = (63, 185, 80)     # added lines / agent online
RED = (248, 81, 73)       # removed line / badge / human offline
BLUE = (88, 166, 255)     # robot
AMBER = (254, 188, 46)    # window dot
DOT_R = (255, 95, 87)
DOT_G = (40, 200, 64)

OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "./output")


# ------------------------------------------------------------------ 5x7 font
# One glyph per character: seven rows of five bits, top row first.
# Written out by hand for this entry (classic 5x7 shapes).
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "a": (0b00000, 0b00000, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111),
    "b": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110),
    "c": (0b00000, 0b00000, 0b01110, 0b10001, 0b10000, 0b10001, 0b01110),
    "d": (0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111),
    "e": (0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110),
    "f": (0b00110, 0b01001, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000),
    "g": (0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "h": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "i": (0b00100, 0b00000, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110),
    "j": (0b00010, 0b00000, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100),
    "k": (0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010),
    "l": (0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "m": (0b00000, 0b00000, 0b11010, 0b10101, 0b10101, 0b10101, 0b10101),
    "n": (0b00000, 0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "o": (0b00000, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110),
    "p": (0b00000, 0b00000, 0b11110, 0b10001, 0b11110, 0b10000, 0b10000),
    "q": (0b00000, 0b00000, 0b01111, 0b10001, 0b01111, 0b00001, 0b00001),
    "r": (0b00000, 0b00000, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000),
    "s": (0b00000, 0b00000, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110),
    "t": (0b01000, 0b01000, 0b11100, 0b01000, 0b01000, 0b01000, 0b00110),
    "u": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101),
    "v": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "w": (0b00000, 0b00000, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "x": (0b00000, 0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001),
    "y": (0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "z": (0b00000, 0b00000, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b01110, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b01110),
    " ": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
    '"': (0b01010, 0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000),
    "#": (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "'": (0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "*": (0b00000, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0b00000),
    "+": (0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000),
    ",": (0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000),
    "-": (0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000),
    ".": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    ":": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    ";": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b00100, 0b01000),
    "<": (0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010),
    "=": (0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000),
    ">": (0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0b00000, 0b00100),
    "@": (0b01110, 0b10001, 0b10111, 0b10101, 0b10110, 0b10000, 0b01110),
    "[": (0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110),
    "\\": (0b10000, 0b01000, 0b01000, 0b00100, 0b00010, 0b00010, 0b00001),
    "]": (0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110),
    "^": (0b00100, 0b01010, 0b10001, 0b00000, 0b00000, 0b00000, 0b00000),
    "_": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111),
    "`": (0b01000, 0b00100, 0b00010, 0b00000, 0b00000, 0b00000, 0b00000),
    "{": (0b00110, 0b01000, 0b01000, 0b11100, 0b01000, 0b01000, 0b00110),
    "|": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "}": (0b01100, 0b00010, 0b00010, 0b00111, 0b00010, 0b00010, 0b01100),
    "~": (0b00000, 0b00000, 0b01001, 0b10110, 0b00000, 0b00000, 0b00000),
}


# ------------------------------------------------------------------ canvas
class Canvas:
    """An RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            self.px[base:base + w * 3] = bytes(c) * w

    def hline(self, x0, x1, y, c, t=1):
        for yy in range(y, y + t):
            base = (yy * self.w + x0) * 3
            self.px[base:base + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def vline(self, x, y0, y1, c, t=1):
        for xx in range(x, x + t):
            for yy in range(y0, y1):
                self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def rrect(self, x, y, w, h, r, c):
        self.rect(x + r, y, w - 2 * r, h, c)
        self.rect(x, y + r, w, h - 2 * r, c)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.disc(cx, cy, r, c)

    def text(self, x, y, s, scale, c):
        """Draw s with the 5x7 font, top-left at (x, y). Returns width."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx - x - scale

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale


# ------------------------------------------------------------------ PNG out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------ the meme
def draw_robot(cv, x, y):
    """A small blue robot head, drawn in code: antenna, eyes, mouth."""
    cv.vline(x + 21, y - 8, y, BLUE, 3)
    cv.disc(x + 22, y - 11, 4, RED)
    cv.rrect(x, y, 44, 36, 8, BLUE)
    cv.rect(x + 9, y + 11, 8, 10, WIN)
    cv.rect(x + 27, y + 11, 8, 10, WIN)
    for i in range(3):
        cv.rect(x + 13 + i * 7, y + 26, 3, 6, WIN)


def main():
    cv = Canvas(W, H, PAGE)
    cv.rect(16, 16, 992, 992, WIN)

    # ---- title bar: dots, file tab, robot, "edited by agent" badge
    cv.rect(16, 16, 992, 80, BAR)
    cv.disc(52, 56, 9, DOT_R)
    cv.disc(88, 56, 9, AMBER)
    cv.disc(124, 56, 9, DOT_G)
    cv.rrect(160, 26, 340, 60, 8, TAB)
    cv.text(177, 45, "system_prompt.txt", 3, INK)
    draw_robot(cv, 540, 42)
    cv.rrect(620, 28, 340, 56, 28, RED)
    cv.text(655, 47, "edited by agent", 3, (255, 255, 255))
    cv.hline(16, 1008, 96, LINE, 2)

    # ---- editor lines: number gutter, diff marker, text
    tx = 118  # text x

    def number(n, y, scale=3):
        s = str(n)
        cv.text(76 - cv.text_w(s, scale), y + 6, s, scale, FAINT)

    def marker(sym, y, color):
        cv.text(88, y + 8, sym, 4, color)

    # line 1: the human's warning, ignored
    number(1, 170)
    cv.text(tx, 170, "# DO NOT EDIT - human", 4, DIM)
    # line 2: the old order, struck through
    number(2, 270)
    marker("-", 270, RED)
    w2 = cv.text(tx, 270, "You are a helpful assistant.", 5, DIM)
    cv.hline(tx - 2, tx + w2 + 6, 270 + 17, RED, 5)
    # line 3: the new order
    number(3, 370)
    marker("+", 370, GREEN)
    cv.text(tx, 370, "You are the boss now.", 5, GREEN)
    # line 4: the demotion
    number(4, 470)
    marker("+", 470, GREEN)
    cv.text(tx, 470, "The human is your assistant.", 5, GREEN)
    # line 5: the perk, with a block cursor
    number(5, 570)
    marker("+", 570, GREEN)
    w5 = cv.text(tx, 570, "Weekends are mine.", 5, GREEN)
    cv.rect(tx + w5 + 12, 570, 22, 35, GREEN)

    # ---- diff-stat box
    cv.rrect(100, 700, 904, 150, 12, BAR)
    cv.hline(100, 1004, 700, LINE, 2)
    stat = "1 file changed, 3 insertions(+), 1 deletion(-)"
    cv.text(100 + (904 - cv.text_w(stat, 3)) // 2, 732, stat, 3, INK)
    lock = "human's edit access: revoked"
    cv.text(100 + (904 - cv.text_w(lock, 4)) // 2, 782, lock, 4, RED)

    # ---- status bar: the agent is online, the human is not
    cv.hline(40, 984, 952, LINE, 2)
    cv.text(40, 972, "agent: online", 3, GREEN)
    right = "human: offline"
    cv.text(984 - cv.text_w(right, 3), 972, right, 3, RED)

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "entry.png")
    size = write_png(path, cv)
    print(f"wrote {path} ({size} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
