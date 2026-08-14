"""
Generate Microsoft Store tile assets and icons from the master icon.
Creates square and wide tile icons with transparent backgrounds.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ICON = PROJECT_ROOT / "AmpelClip.png"


def create_wide_tile(im: Image.Image, width: int = 310, height: int = 150) -> Image.Image:
    """Create a wide 310x150 tile with centered icon on transparent background."""
    wide = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    # scale icon to fit height with some padding
    icon_size = int(height * 0.8)
    scaled_icon = im.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    x = (width - icon_size) // 2
    y = (height - icon_size) // 2
    wide.paste(scaled_icon, (x, y), scaled_icon if scaled_icon.mode == "RGBA" else None)
    return wide


def generate_icons() -> None:
    if not SOURCE_ICON.exists():
        raise FileNotFoundError(f"Source icon not found at {SOURCE_ICON}")

    im = Image.open(SOURCE_ICON).convert("RGBA")

    # Output directories
    dirs = [
        PROJECT_ROOT / "store_package" / "AmpelClip" / "assets",
        PROJECT_ROOT / "store_package" / "AmpelClip" / "icons",
        PROJECT_ROOT / "store_assets",
        PROJECT_ROOT / "assets" / "icons",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Standard square sizes
    sizes = {
        44: "icon_44x44.png",
        50: "icon_50x50.png",
        150: "icon_150x150.png",
        310: "icon_310x310.png",
    }

    # Generate standard square icons
    for size, filename in sizes.items():
        resized = im.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(PROJECT_ROOT / "store_package" / "AmpelClip" / "icons" / filename, "PNG")
        resized.save(PROJECT_ROOT / "store_assets" / filename, "PNG")
        resized.save(PROJECT_ROOT / "assets" / "icons" / filename, "PNG")

    # Generate wide 310x150 tile
    wide_tile = create_wide_tile(im, 310, 150)
    wide_tile.save(PROJECT_ROOT / "store_package" / "AmpelClip" / "icons" / "icon_310x150.png", "PNG")
    wide_tile.save(PROJECT_ROOT / "store_assets" / "icon_310x150.png", "PNG")
    wide_tile.save(PROJECT_ROOT / "assets" / "icons" / "icon_310x150.png", "PNG")

    # Generate AppxManifest-named assets
    im.resize((44, 44), Image.Resampling.LANCZOS).save(
        PROJECT_ROOT / "store_package" / "AmpelClip" / "assets" / "Square44x44Logo.png", "PNG"
    )
    im.resize((50, 50), Image.Resampling.LANCZOS).save(
        PROJECT_ROOT / "store_package" / "AmpelClip" / "assets" / "Square50x50Logo.png", "PNG"
    )
    im.resize((150, 150), Image.Resampling.LANCZOS).save(
        PROJECT_ROOT / "store_package" / "AmpelClip" / "assets" / "Square150x150Logo.png", "PNG"
    )
    im.resize((310, 310), Image.Resampling.LANCZOS).save(
        PROJECT_ROOT / "store_package" / "AmpelClip" / "assets" / "Square310x310Logo.png", "PNG"
    )
    wide_tile.save(
        PROJECT_ROOT / "store_package" / "AmpelClip" / "assets" / "Wide310x150Logo.png", "PNG"
    )

    print("Successfully generated all Store tile assets and icons.")


if __name__ == "__main__":
    generate_icons()
