from pathlib import Path

from pytiled_parser import common_types, layer, tiled_object

EXPECTED = [
    layer.TileLayer(
        name="Tile Layer 1",
        opacity=1,
        visible=True,
        id=1,
        size=common_types.Size(8, 6),
        data=[
            [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
            ],
            [
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
            ],
            [
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
            ],
            [
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
            ],
            [
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
            ],
            [
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
            ],
        ],
    ),
    layer.LayerGroup(
        name="Group 1",
        opacity=1,
        visible=True,
        id=4,
        layers=[
            layer.ObjectLayer(
                name="Object Layer 1",
                opacity=1,
                visible=True,
                id=2,
                draw_order="topdown",
                tiled_objects=[
                    tiled_object.Rectangle(
                        id=1,
                        name="",
                        rotation=0,
                        size=common_types.Size(69.3333333333333, 52.6666666666667),
                        coordinates=common_types.OrderedPair(46.3333333333333, 39),
                        visible=True,
                        class_="",
                    )
                ],
            ),
        ],
    ),
    layer.ImageLayer(
        name="Image Layer 1",
        opacity=1,
        visible=True,
        id=3,
        image=Path("../../images/tile_04.png"),
        transparent_color=common_types.Color(0, 0, 0, 255),
    ),
]
