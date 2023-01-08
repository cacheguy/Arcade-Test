from pathlib import Path

from pytiled_parser import tileset

EXPECTED = tileset.Tileset(
    columns=8,
    image=Path("../../images/tmw_desert_spacing.png"),
    image_height=199,
    image_width=265,
    firstgid=1,
    margin=1,
    spacing=1,
    name="tile_set_image",
    tile_count=48,
    tiled_version="1.9.2",
    tile_height=32,
    tile_width=32,
    tiles={
        0: tileset.Tile(
            id=0,
            properties={
                "Test": "test property"
            }
        )
    },
    version="1.9",
    type="tileset",
    alignment="topleft",
    tile_render_size="grid",
    fill_mode="preserve-aspect-fit"
)
