from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICON_PNG = ASSETS / "typeflow-icon.png"
ICON_ICO = ASSETS / "typeflow.ico"
TRAY_PNG = ASSETS / "typeflow-tray.png"


def build_icon(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    base_margin = int(size * 0.08)
    draw.rounded_rectangle(
        (base_margin, base_margin, size - base_margin, size - base_margin),
        radius=int(size * 0.24),
        fill="#0f2236",
    )

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(
        (base_margin + 6, base_margin + 6, size - base_margin - 6, size - base_margin - 6),
        radius=int(size * 0.22),
        outline="#1eb6c9",
        width=max(2, size // 32),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(2, size // 40)))
    image.alpha_composite(glow)
    draw = ImageDraw.Draw(image)

    wave_left = int(size * 0.18)
    wave_right = int(size * 0.82)
    mid_y = int(size * 0.35)
    bar_width = max(6, size // 22)
    gap = max(5, size // 36)
    heights = (0.12, 0.22, 0.34, 0.22, 0.12)
    for index, factor in enumerate(heights):
        x0 = wave_left + index * (bar_width + gap)
        x1 = x0 + bar_width
        height = int(size * factor)
        y0 = mid_y - height // 2
        y1 = mid_y + height // 2
        draw.rounded_rectangle((x0, y0, x1, y1), radius=bar_width // 2, fill="#3dd6e9")

    capsule_width = int(size * 0.20)
    capsule_height = int(size * 0.32)
    capsule_x0 = (size - capsule_width) // 2
    capsule_y0 = int(size * 0.36)
    capsule_x1 = capsule_x0 + capsule_width
    capsule_y1 = capsule_y0 + capsule_height
    draw.rounded_rectangle(
        (capsule_x0, capsule_y0, capsule_x1, capsule_y1),
        radius=capsule_width // 2,
        fill="#f8fbff",
    )
    draw.rectangle(
        (size * 0.47, size * 0.64, size * 0.53, size * 0.78),
        fill="#f8fbff",
    )
    draw.arc(
        (size * 0.34, size * 0.48, size * 0.66, size * 0.83),
        start=205,
        end=-25,
        fill="#f8fbff",
        width=max(3, size // 28),
    )
    draw.rounded_rectangle(
        (size * 0.40, size * 0.79, size * 0.60, size * 0.84),
        radius=max(3, size // 50),
        fill="#f8fbff",
    )

    return image


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)

    icon_1024 = build_icon(1024)
    icon_1024.save(ICON_PNG)
    icon_1024.resize((256, 256), Image.Resampling.LANCZOS).save(TRAY_PNG)

    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    icon_1024.save(ICON_ICO, sizes=sizes)

    print(f"Generated {ICON_PNG}")
    print(f"Generated {TRAY_PNG}")
    print(f"Generated {ICON_ICO}")


if __name__ == "__main__":
    main()
