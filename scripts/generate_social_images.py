#!/usr/bin/env python3
"""Generate the brand image and social preview. Requires Pillow."""

from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCALE = 2
NIGHT = "#08111f"
WHITE = "#f4f7fc"
BLUE = "#a9c8ef"
MUTED = "#a8bbd3"


def px(value: int | float) -> int:
    return round(value * SCALE)


def font(size: int, serif: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    choices = (
        ["/System/Library/Fonts/Supplemental/Georgia.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
        if serif else
        ["/System/Library/Fonts/Avenir Next.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for choice in choices:
        if Path(choice).exists():
            return ImageFont.truetype(choice, px(size))
    return ImageFont.load_default()


def orbit(cx: float, cy: float, rx: float, ry: float, angle: float) -> list[tuple[int, int]]:
    points = []
    for step in range(361):
        theta = step * pi / 180
        x = rx * cos(theta)
        y = ry * sin(theta)
        points.append((px(cx + x * cos(angle) - y * sin(angle)), px(cy + x * sin(angle) + y * cos(angle))))
    return points


def downsample(image: Image.Image, name: str, size: tuple[int, int]) -> None:
    image.resize(size, Image.Resampling.LANCZOS).save(ASSETS / name, optimize=True)


def social_card() -> None:
    image = Image.new("RGB", (px(1200), px(630)), NIGHT)
    draw = ImageDraw.Draw(image)
    for x in range(64, 1200, 40):
        for y in range(54, 630, 40):
            draw.ellipse((px(x), px(y), px(x + 1), px(y + 1)), fill="#17283f")

    # Brand mark.
    draw.line([(px(82), px(94)), (px(82), px(47)), (px(122), px(47))], fill=WHITE, width=px(3))
    draw.line([(px(82), px(70)), (px(111), px(70))], fill=WHITE, width=px(3))
    draw.arc((px(103), px(46), px(144), px(91)), -75, 110, fill=BLUE, width=px(2))
    draw.ellipse((px(137), px(65), px(143), px(71)), fill=BLUE)
    draw.text((px(154), px(43)), "Feynman Lab", font=font(27), fill=WHITE)

    draw.text((px(82), px(174)), "Ideas into", font=font(108, serif=True), fill=WHITE)
    draw.text((px(82), px(281)), "reality.", font=font(113, serif=True), fill=BLUE)
    draw.line((px(82), px(499), px(670), px(499)), fill="#294260", width=px(1))
    draw.text((px(82), px(525)), "Small ideas. Useful software.", font=font(25), fill=MUTED)

    # Scientific diagram, deliberately quieter than the headline.
    center = (960, 304)
    for radius in (118, 170, 221):
        draw.ellipse((px(center[0] - radius), px(center[1] - radius), px(center[0] + radius), px(center[1] + radius)), outline="#203650", width=px(1))
    draw.line(orbit(*center, 212, 103, -.46), fill="#53769f", width=px(2), joint="curve")
    draw.line(orbit(*center, 163, 72, .75), fill="#8db7e8", width=px(2), joint="curve")
    for x, y, radius in ((748, 362, 7), (1080, 201, 8), (1001, 438, 5)):
        draw.ellipse((px(x-radius), px(y-radius), px(x+radius), px(y+radius)), fill=BLUE)
    draw.ellipse((px(951), px(295), px(969), px(313)), fill=NIGHT, outline=BLUE, width=px(2))
    downsample(image, "og-image.png", (1200, 630))


def logo() -> None:
    image = Image.new("RGB", (px(512), px(512)), NIGHT)
    draw = ImageDraw.Draw(image)
    draw.line([(px(148), px(374)), (px(148), px(140)), (px(340), px(140))], fill=WHITE, width=px(20), joint="curve")
    draw.line([(px(148), px(254)), (px(286), px(254))], fill=WHITE, width=px(20))
    draw.arc((px(243), px(138), px(402), px(374)), -76, 112, fill=BLUE, width=px(12))
    draw.ellipse((px(372), px(240), px(402), px(270)), fill=BLUE)
    downsample(image, "logo-512.png", (512, 512))


if __name__ == "__main__":
    social_card()
    logo()
    print("Generated social preview and organization logo")
