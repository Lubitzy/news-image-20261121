"""Render original news illustrations; the submitted program needs no Pillow.

Run with an installed Pillow build and local Arial/DejaVu fonts. No downloads,
network calls, external images, logos, or competitor assets are used.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
SCALE = 2
PAPER = "#F4F0E7"
INK = "#153541"
MUTED = "#53656B"
WHITE = "#FFFEFB"
RULE = "#D9DED8"

FONT_PATHS = {
    "regular": ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "bold": ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "serif": ["C:/Windows/Fonts/georgiab.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
}


@lru_cache(maxsize=128)
def font(size: int, style: str = "regular") -> ImageFont.FreeTypeFont:
    for filename in FONT_PATHS[style]:
        if Path(filename).is_file():
            return ImageFont.truetype(filename, round(size * SCALE))
    raise RuntimeError(f"Install a local font for {style}; see FONT_PATHS")


@dataclass(frozen=True)
class Story:
    key: str
    region: str
    title: str
    deck: str
    sources: str
    color: str


STORIES = [
    Story("bridge", "EUROPE / UKRAINE", "Kyiv bridges hit",
          "Officials: Russian strikes kill 8 across Ukraine.",
          "Reuters + AP", "#306B94"),
    Story("climate", "GLOBAL / CLIMATE", "COP31 deadlock",
          "Draft omits fossil fuels; Antalya talks unresolved.",
          "AFP + AP", "#24786E"),
    Story("markets", "US / MARKETS", "Tech stocks slide",
          "Nasdaq −5.3% / S&P 500 −3.7% at US close.",
          "Reuters + AP", "#665B8D"),
    Story("trade", "ASIA / TRADE", "35 trade MoUs",
          "Indonesia + China sign $15bn in MoUs.",
          "ANTARA + Reuters", "#8A6A2B"),
    Story("port", "MIDDLE EAST / YEMEN", "Yemen port struck",
          "Hodeidah struck, Saudi-led coalition says.",
          "Reuters + AP", "#AD5944"),
    Story("food", "GLOBAL / AID", "Food aid appeal",
          "WFP seeks $12bn+ to assist 91m in 2027.",
          "Reuters + Anadolu", "#637C43"),
]


class Painter:
    def __init__(self, color: str):
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), color)
        self.draw = ImageDraw.Draw(self.image)
        self.text_checks: list[dict] = []
        self.layout_checks: list[dict] = []

    @staticmethod
    def box(box):
        return tuple(round(n * SCALE) for n in box)

    def rect(self, box, fill, outline=None, width: float = 1, radius: float = 0):
        coords = self.box(box)
        if radius:
            self.draw.rounded_rectangle(coords, radius=round(radius * SCALE),
                                        fill=fill, outline=outline, width=round(width * SCALE))
        else:
            self.draw.rectangle(coords, fill=fill, outline=outline, width=round(width * SCALE))

    def ellipse(self, box, fill=None, outline=None, width: float = 1):
        self.draw.ellipse(self.box(box), fill=fill, outline=outline, width=round(width * SCALE))

    def line(self, points, fill, width: float = 1):
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                       fill=fill, width=max(1, round(width * SCALE)), joint="curve")

    def polygon(self, points, fill):
        self.draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=fill)

    def text(self, xy, text, size, fill=INK, style="regular"):
        self.draw.text((round(xy[0] * SCALE), round(xy[1] * SCALE)), text,
                       font=font(size, style), fill=fill, anchor="lt")

    def wrapped(self, xy, text, size, width, fill=INK, style="regular", max_lines=4):
        words = text.split()
        lines, line = [], ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if font(size, style).getlength(candidate) / SCALE <= width:
                line = candidate
            else:
                if not line:
                    raise ValueError(f"A word does not fit: {word}")
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        if len(lines) > max_lines:
            raise ValueError(f"Too many lines ({len(lines)}): {text}")
        height = round(size * 1.16)
        for index, item in enumerate(lines):
            self.text((xy[0], xy[1] + index * height), item, size, fill, style)
        self.text_checks.append({"text": text, "lines": len(lines), "font_px": size,
                                 "box": [xy[0], xy[1], width, height * len(lines)]})
        return len(lines) * height


def icon(p: Painter, key: str, x: float, y: float, w: float, h: float, color: str):
    """All geometry below is authored here in a 160 by 120 coordinate system."""
    def point(a, b):
        return x + a * w / 160, y + b * h / 120

    def line(points, shade=color, weight=4):
        p.line([point(a, b) for a, b in points], shade, weight * min(w / 160, h / 120))

    def rect(a, b, c, d, shade, outline=None, weight=2, radius=0):
        p.rect((*point(a, b), *point(c, d)), shade, outline,
               weight * min(w / 160, h / 120), radius * min(w / 160, h / 120))

    def oval(a, b, c, d, shade=None, outline=color, weight=3):
        p.ellipse((*point(a, b), *point(c, d)), shade, outline,
                  weight * min(w / 160, h / 120))

    def poly(points, shade=color):
        p.polygon([point(a, b) for a, b in points], shade)

    pale = "#DCE9E6"
    if key == "bridge":
        for base in (100, 112):
            line([(10, base), (35, base - 4), (60, base), (85, base - 4), (110, base), (150, base - 4)], "#94BCCB", 3)
        line([(12, 82), (148, 82)], weight=7)
        for tower in (43, 116):
            rect(tower - 4, 26, tower + 4, 99, color)
            for anchor in (15, 79, 147):
                line([(tower, 30), (anchor, 81)], weight=2)
        line([(73, 78), (81, 86), (88, 77)], "#AD5944", 5)
        for a in (0, 1, 2):
            angle = -math.pi / 2 + a * math.pi / 3
            line([(82 + 14 * math.cos(angle), 22 + 14 * math.sin(angle)),
                  (82 + 25 * math.cos(angle), 22 + 25 * math.sin(angle))], "#AD5944", 3)
    elif key == "climate":
        oval(35, 5, 126, 96, pale, color, 4)
        oval(62, 5, 99, 96, None, color, 2)
        line([(37, 51), (124, 51)], weight=2)
        line([(44, 29), (116, 29)], weight=2)
        line([(44, 73), (116, 73)], weight=2)
        rect(88, 65, 153, 103, WHITE, color, 3, 8)
        poly([(102, 101), (96, 115), (119, 102)])
        line([(103, 78), (137, 78)], weight=3)
        line([(103, 91), (125, 91)], weight=3)
    elif key == "markets":
        # These two bars encode the reported daily losses, not an invented timeline.
        zero = 25
        line([(12, zero), (149, zero)], "#8B97A5", 2)
        for center, loss in ((52, 5.3), (108, 3.7)):
            rect(center - 16, zero, center + 16, zero + loss * 14, color)
        line([(16, 9), (16, 108)], "#8B97A5", 2)
        p.text(point(41, 103), "N", max(12, round(w * .11)), color, "bold")
        p.text(point(96, 85), "S", max(12, round(w * .11)), color, "bold")
    elif key == "trade":
        for left, top in ((17, 13), (88, 28)):
            rect(left, top, left + 55, top + 77, WHITE, color, 3, 5)
            poly([(left + 37, top), (left + 55, top + 18), (left + 37, top + 18)], pale)
            for off in (30, 43, 56):
                line([(left + 10, top + off), (left + 40, top + off)], weight=2)
        line([(53, 100), (67, 112), (104, 78)], "#24786E", 7)
    elif key == "port":
        rect(108, 10, 114, 83, color)
        line([(111, 12), (55, 48), (132, 12)], weight=5)
        line([(57, 47), (57, 61)], weight=2)
        for left, shade in ((28, pale), (57, color), (86, pale)):
            rect(left, 59, left + 25, 80, shade, color, 2)
        poly([(15, 84), (137, 84), (123, 103), (35, 103)])
        for base in (108, 117):
            line([(9, base), (33, base - 3), (56, base), (80, base - 3), (104, base), (148, base - 4)], "#94BCCB", 3)
    elif key == "food":
        oval(30, 62, 133, 117, color, color, 3)
        rect(24, 91, 138, 120, PAPER)
        line([(31, 65), (46, 96), (117, 96), (132, 65)], weight=4)
        line([(31, 65), (133, 65)], weight=5)
        line([(81, 14), (81, 61)], weight=3)
        for level in (24, 38, 51):
            oval(60, level - 8, 79, level + 4, pale, color, 2)
            oval(84, level - 8, 103, level + 4, pale, color, 2)
        line([(72, 103), (97, 103)], weight=4)
    else:
        raise ValueError(key)


def masthead(p: Painter, dark=False):
    foreground = WHITE if dark else INK
    secondary = "#A8C7CC" if dark else MUTED
    p.text((42, 25), "THE WORLD / SIX STORIES", 20, secondary, "bold")
    p.text((39, 65), "20 November 2026", 79, foreground, "bold")
    p.text((43, 158), "ONE DAY. SIX DEVELOPMENTS.", 20, secondary, "bold")
    p.line([(42, 194), (982, 194)], "#517078" if dark else INK, 2)


def footer(p: Painter, dark=False):
    shade = "#A8C7CC" if dark else MUTED
    p.line([(42, 956), (982, 956)], "#517078" if dark else RULE, 1)
    p.text((43, 971), "AS REPORTED ON 20 NOV / CLAIMS ATTRIBUTED", 17, shade, "bold")
    p.text((43, 998), "Original illustrations  ·  Full sources and qualifications in NOTES.md", 14, shade)


def card(p: Painter, story: Story, box, lead=False, dark=False):
    x, y, w, h = box
    p.rect((x, y, x + w, y + h), "#193D49" if dark else WHITE,
           "#3E6069" if dark else RULE, 1, 12)
    p.rect((x, y + 14, x + 5, y + h - 14), story.color, radius=2)
    shade = "#F2F6F0" if dark else INK
    body = "#C8D9D9" if dark else MUTED
    p.text((x + 21, y + 17), story.region, 17, "#D3DCD4" if dark else story.color, "bold")
    if lead:
        icon(p, story.key, x + w - 161, y + 55, 142, 111, story.color)
        title_height = p.wrapped((x + 22, y + 57), story.title, 42, w - 180,
                                 shade, "bold", 2)
        deck_y = y + max(169, title_height + 78)
        deck_height = p.wrapped((x + 23, deck_y), story.deck, 27, w - 46, body, max_lines=3)
        title_bottom = y + 57 + title_height
    else:
        icon(p, story.key, x + w - 90, y + 7, 70, 52, story.color)
        title_y = y + (48 if h < 220 else 62)
        title_height = p.wrapped((x + 23, title_y), story.title, 34 if h < 220 else 42,
                                 w - 46, shade, "bold", 1)
        title_bottom = title_y + title_height
        deck_y = y + (105 if h < 220 else 125)
        deck_height = p.wrapped((x + 23, deck_y), story.deck, 26 if h < 220 else 32,
                                w - 46, body, max_lines=2)
    source_y = y + h - 23
    source_gap = source_y - (deck_y + deck_height)
    title_gap = deck_y - title_bottom
    if source_gap < 8 or title_gap < 8:
        raise ValueError(f"Text overlap in {story.key}: title gap {title_gap}, source gap {source_gap}")
    p.layout_checks.append({"story": story.key, "title_gap_px": title_gap,
                            "source_gap_px": source_gap, "card": list(box)})
    p.text((x + 23, source_y), story.sources, 17, body)


def render(variant: str, output: Path):
    p = Painter("#102F3A" if variant == "C" else PAPER)
    masthead(p, variant == "C")
    if variant == "B":
        for index, story in enumerate(STORIES[:2]):
            card(p, story, (42 + index * 478, 212, 462, 290), lead=True)
        for index, story in enumerate(STORIES[2:]):
            row, col = divmod(index, 2)
            card(p, story, (42 + col * 478, 518 + row * 218, 462, 202))
    elif variant in ("A", "C"):
        for index, story in enumerate(STORIES):
            row, col = divmod(index, 2)
            card(p, story, (42 + col * 478, 212 + row * 247, 462, 231), dark=variant == "C")
    else:
        raise ValueError(variant)
    footer(p, variant == "C")
    output.parent.mkdir(parents=True, exist_ok=True)
    final = p.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    final.save(output, format="PNG", optimize=True, compress_level=9)
    thumbnail = output.with_name(output.stem + "-300.png")
    final.resize((300, 300), Image.Resampling.LANCZOS).save(thumbnail, format="PNG", optimize=True)
    return {"variant": variant, "output": str(output), "bytes": output.stat().st_size,
            "thumbnail": str(thumbnail), "text_boxes": p.text_checks,
            "layout_checks": p.layout_checks,
            "font_files": {style: next(path for path in paths if Path(path).is_file())
                           for style, paths in FONT_PATHS.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=["A", "B", "C", "all"], default="all")
    parser.add_argument("--out-dir", type=Path, default=Path("designs"))
    args = parser.parse_args()
    variants = ("A", "B", "C") if args.variant == "all" else (args.variant,)
    reports = [render(item, args.out_dir / f"variant-{item}.png") for item in variants]
    (args.out_dir / "render-report.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(json.dumps([{k: value for k, value in report.items() if k not in ("text_boxes", "layout_checks")}
                      for report in reports], indent=2))


if __name__ == "__main__":
    main()
