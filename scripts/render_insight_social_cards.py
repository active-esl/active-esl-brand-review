#!/usr/bin/env python3
"""Render 1200×627 Open Graph cards for Active-Edge Insights."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images" / "insights"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1200, 627
CARBON = "#07111F"
CARBON_2 = "#101E31"
CLOUD = "#F7F9FC"
MUTED = "#A8B4C5"
CYAN = "#20D6D2"
VIOLET = "#7557FF"
LIME = "#B6F23B"

SORA = Path.home() / ".fonts" / "Sora-ExtraBold.ttf"
SPACE = Path.home() / ".fonts" / "SpaceGrotesk-Medium.ttf"
PLEX = Path.home() / ".fonts" / "IBMPlexSans-Regular.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def gradient_background() -> Image.Image:
    image = Image.new("RGB", (W, H), CARBON)
    pixels = image.load()
    for y in range(H):
        for x in range(W):
            # Restrained cyan/violet lift toward the visual side.
            dx, dy = (x - 1000) / 720, (y - 250) / 520
            glow = max(0.0, 1.0 - (dx * dx + dy * dy))
            violet = max(0.0, 1.0 - (((x - 950) / 900) ** 2 + ((y - 650) / 700) ** 2))
            base = (7, 17, 31)
            pixels[x, y] = (
                int(base[0] + 12 * glow + 9 * violet),
                int(base[1] + 18 * glow + 4 * violet),
                int(base[2] + 28 * glow + 22 * violet),
            )
    return image


def draw_brand(draw: ImageDraw.ImageDraw) -> None:
    draw.text((64, 46), "ACTIVE-EDGE", font=font(SPACE, 23), fill=CLOUD)
    draw.text((64, 80), "EMBEDDED INTELLIGENCE. MADE REAL.", font=font(SPACE, 12), fill=MUTED)
    draw.rounded_rectangle((64, 117, 160, 121), radius=2, fill=CYAN)
    draw.rounded_rectangle((160, 117, 224, 121), radius=2, fill=VIOLET)
    draw.rounded_rectangle((224, 117, 270, 121), radius=2, fill=LIME)


def fit_lines(draw: ImageDraw.ImageDraw, text: str, max_width: int, size: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    face = font(SORA, size)
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_heading(draw: ImageDraw.ImageDraw, title: str, deck: str) -> None:
    draw.text((64, 160), "INSIGHTS", font=font(SPACE, 17), fill=CYAN)
    lines = fit_lines(draw, title, 700, 50)
    y = 200
    for line in lines:
        draw.text((64, y), line, font=font(SORA, 50), fill=CLOUD)
        y += 61
    draw.multiline_text((64, y + 20), deck, font=font(PLEX, 22), fill=MUTED, spacing=8)
    draw.text((64, 562), "active-esl.com/insights", font=font(SPACE, 16), fill=CLOUD)


def draw_working_relationship() -> None:
    image = gradient_background()
    draw = ImageDraw.Draw(image)
    draw_brand(draw)
    draw_heading(
        draw,
        "Not a harness. A working relationship.",
        "How humans and agents work together\nwhen the stakes are real.",
    )

    # Two accountable parties connected by a bright working edge.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line((815, 260, 1030, 405), fill=(32, 214, 210, 120), width=24)
    gd.ellipse((782, 227, 848, 293), fill=(117, 87, 255, 210))
    gd.ellipse((997, 372, 1063, 438), fill=(182, 242, 59, 210))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(glow) if image.mode == "RGBA" else image.paste(glow, mask=glow)

    draw = ImageDraw.Draw(image)
    draw.line((815, 260, 1030, 405), fill=CYAN, width=6)
    for cx, cy, colour, label in (
        (815, 260, VIOLET, "HUMAN"),
        (1030, 405, LIME, "AGENT"),
    ):
        draw.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=CARBON_2, outline=colour, width=5)
        bbox = draw.textbbox((0, 0), label, font=font(SPACE, 14))
        draw.text((cx - (bbox[2] - bbox[0]) / 2, cy + 48), label, font=font(SPACE, 14), fill=CLOUD)
    draw.rounded_rectangle((855, 309, 990, 356), radius=23, fill=CARBON_2, outline=CYAN, width=2)
    draw.text((882, 321), "TRUST + GATES", font=font(SPACE, 13), fill=CLOUD)

    image.save(OUT / "not-a-harness-working-relationship-og.png", optimize=True)


def draw_zephyr_budget() -> None:
    image = gradient_background()
    draw = ImageDraw.Draw(image)
    draw_brand(draw)
    draw_heading(
        draw,
        "Zephyr quality needs a vendor budget line.",
        "Fund review, driver quality and release capacity.",
    )

    draw.rounded_rectangle((785, 175, 1135, 480), radius=28, fill=CARBON_2, outline=VIOLET, width=3)
    draw.text((827, 205), "ABOUT", font=font(SPACE, 18), fill=MUTED)
    draw.text((827, 235), "1,700", font=font(SORA, 78), fill=CYAN)
    draw.text((845, 330), "OPEN PRs", font=font(SPACE, 30), fill=CLOUD)
    draw.line((835, 371, 1085, 371), fill="#2C3D54", width=2)
    draw.text((833, 399), "CAPACITY SIGNAL", font=font(SPACE, 18), fill=LIME)

    image.save(OUT / "zephyr-vendor-budget-og.png", optimize=True)


def draw_insights_index() -> None:
    image = gradient_background()
    draw = ImageDraw.Draw(image)
    draw_brand(draw)
    draw_heading(
        draw,
        "Field notes from the edge.",
        "Connected products, manufacture and\nengineering practice when the stakes are real.",
    )

    for x, y, colour in ((835, 245, CYAN), (995, 320, VIOLET), (875, 430, LIME)):
        draw.rounded_rectangle((x - 18, y - 18, x + 18, y + 18), radius=8, fill=CARBON_2, outline=colour, width=4)
    draw.line((853, 254, 977, 311), fill=CYAN, width=5)
    draw.line((980, 338, 892, 415), fill=VIOLET, width=5)
    draw.line((850, 427, 748, 360), fill=LIME, width=5)
    draw.text((754, 334), "REAL WORK", font=font(SPACE, 15), fill=CLOUD)

    image.save(OUT / "active-edge-insights-og.png", optimize=True)


def draw_metric_story(filename: str, title: str, deck: str, value: str, label: str, footer: str) -> None:
    image = gradient_background()
    draw = ImageDraw.Draw(image)
    draw_brand(draw)
    draw_heading(draw, title, deck)

    draw.rounded_rectangle((805, 180, 1135, 485), radius=28, fill=CARBON_2, outline=VIOLET, width=3)
    value_box = draw.textbbox((0, 0), value, font=font(SORA, 68))
    draw.text((970 - (value_box[2] - value_box[0]) / 2, 225), value, font=font(SORA, 68), fill=CYAN)
    label_box = draw.textbbox((0, 0), label, font=font(SPACE, 20))
    draw.text((970 - (label_box[2] - label_box[0]) / 2, 320), label, font=font(SPACE, 20), fill=CLOUD)
    draw.line((845, 374, 1095, 374), fill="#2C3D54", width=2)
    footer_box = draw.textbbox((0, 0), footer, font=font(SPACE, 16))
    draw.text((970 - (footer_box[2] - footer_box[0]) / 2, 405), footer, font=font(SPACE, 16), fill=LIME)

    image.save(OUT / filename, optimize=True)


if __name__ == "__main__":
    draw_insights_index()
    draw_working_relationship()
    draw_zephyr_budget()
    draw_metric_story(
        "colour-eink-better-bring-up-og.png",
        "A colour e-ink platform, and a better way to bring it up.",
        "Low-power display meets a faster remote workflow.",
        "5-YEAR",
        "BATTERY TARGET",
        "i.MX93 + SECURE OTA",
    )
    draw_metric_story(
        "remote-hardware-lab-og.png",
        "When the hardware lab becomes part of the product platform.",
        "Real boards, controlled power and evidence from anywhere.",
        "REMOTE",
        "REAL HARDWARE",
        "BUILD · DEPLOY · OBSERVE",
    )
    draw_metric_story(
        "ten-prototypes-secure-linux-og.png",
        "Ten prototypes to secure Linux in about ten minutes.",
        "The visible return on a reusable embedded platform.",
        "10",
        "PROTOTYPES",
        "ABOUT 10 MIN · FIRST BOOT",
    )
    for path in sorted(OUT.glob("*-og.png")):
        with Image.open(path) as image:
            print(f"{path.relative_to(ROOT)} {image.width}×{image.height} {path.stat().st_size} bytes")
