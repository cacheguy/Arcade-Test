# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [2.2.0] - 2022-08-13

Added support for the following features from Tiled which were added in either Tiled 1.8 or 1.9. If you would like some more info on some of these items, please refer to the [release notes](https://www.mapeditor.org/news) from Tiled for those versions:

- **Tilesets**
    
    - `Tileset.tile_render_size` has been added, which reflects the `tilerendersize` attribute from Tiled. This is a string value which can be either "tile" or "grid". This is used to determine the size the tile will render at. This defaults to `tile` and is the only behavior prior to Tiled 1.9, meaning it will use the size specified by the Tile. If this is set to `grid` it will scale the tiles to the size defined the grid in the map.
    - `Tileset.fill_mode` has been added, which reflects the `fillmode` attribute from Tiled. This is a string value which can be either "stretch" or "preserve-aspect-ratio". This is used to define how the scaling will be done when a tile is not rendered at it's native size(Like when using the `grid` option for `tilerendersize`).
    - The `Tile` class has four new attributes: `x`, `y`, `width`, and `height`. By default, `x` and `y` will be zero, and `width` and `height` will be the same as `image_width` and `image_height`. These values are only able to changed for tiles which use an individual image rather than a single image file for the whole tileset. These values are used to define a sub-rectangle of the image which the Tile should be loaded as. These are all separate attributes rather than using the `OrderedPair` and `Size` classes as this is somewhat of a developing feature in Tiled in an effort to support sprite atlasses, and so for now we are going to just stick as closely to the underlying format as possible for it, to make future changes easier.
    
- **Layers**

    - Added `repeat_x` and `repeat_y` attributes. These are derived from the `repeatx` and `repeaty` attributes in Tiled. These are boolean values which are used to determine if a layer should be repeated on a given axis when drawn. As of writing in Tiled these values can only be applied to Image layers, however it is possible other types will support this in the future. To prepare for this, these values are available to all layer types in pytiled_parser, and they will default to `False`.

- **Maps**

    - Added `parallax_origin` attribute. This is an `OrderedPair` object which is derived from the `parallaxoriginx` and `parallaxoriginy` attributes in Tiled. This is used to define a map wide origin point that layers which have parallax scrolling will use.


## [2.1.2] - 2022-08-10

This version does not make any changes to the library. The project has moved to using Github Actions to publishing the distribution to PyPI. We have made this release to fully test the system and ensure it is functional for future releases.

## [2.1.1] - 2022-08-10

This version contains just one bug fix. Previously if a map or other object in the TMX format contained a [Class property](https://doc.mapeditor.org/en/stable/manual/custom-properties/#custom-types) which was added in Tiled 1.8, then pytiled-parser would crash.

Classes are not a supported feature in pytiled-parser yet, however the existence of them isn't intended to break the rest of the supported featureset. This fix makes the rest of the map still be able to be successfully parsed and used if one of these exists in it.

See [#60](https://github.com/pythonarcade/pytiled_parser/pull/60) for more info on this bug. Thanks to [laqieer](https://github.com/laqieer) for this PR.

## [2.1.0] - 2022-08-02

This is largely a compatibility update to work with the latest version of Tiled. This version represents the first version of pytiled-parser that is compatible with the formats from Tiled 1.9. Previous versions do not work with maps or tilesets of either JSON or TMX formats from Tiled 1.9 or higher, if you need to use Tiled 1.9+ with an older version of Tiled, you will need to use Tiled's ability to save the map in compatibility mode.

This update does introduce a slight API breaking change, but is unlikely to really cause any problems. The `type` attribute has been removed from the `TiledObject` class as well as the `Tile` class. It has been replaced with the `class_` attribute. This is in keeping with following Tiled's own API as closely as possible. There shouldn't really be any functional difference here, in most cases it has just been re-named. For more information on this change, you can reference the [Tiled JSON format changelog](https://doc.mapeditor.org/en/stable/reference/json-map-format/#changelog).

It is important to note, that this update does not add support for new features introduced in Tiled 1.9(and in fact, we are still missing support for some features from 1.8). This update is primarily to ensure that maps using the base feature set we have had support for will continue to work with the same supported featureset on Tiled 1.9. Support for the new features is something we would like to achieve, but we did not want to hold back general compatibility for it.

Outside of that, all other changes are to the internal parsers and do not effect usage/implementation of pytiled-parser.

## [2.0.1] - 2021-12-21

Someone, not naming any names, forgot to put `__init__.py` files in some packages, and caused imports to break when installed via a `.whl` and not an editable source install. This just fixes that problem.

## [2.0.0] - 2021-12-21

Welcome to pytiled-parser 2.0! A lot has changed under the hood with this release that has enabled a slew of new features and abilities. Most of the changes here are under the hood, and there is only really one major API change to be aware of. However the under the hood changes and the new features they've enabled are significant enough to call this a major release.

The entire pytiled-parser API has been abstracted to a common interface, and the parsing functionality completely
seperated from it. This means that we are able to implement parsers for different formats, and enable cross-loading between formats.

With the release of 2.0, we have added full support for the TMX spec. Meaning you can once again load TMX maps, TSX tilesets, and TX templates with pytiled-parser, just like the pre 1.0 days, except now we have 100% coverage of the spec, and it's behind the same 1.0 API interface you've come to know and love.

If you're already using pytiled-parser, chances are you don't need to do anything other than upgrade to enable TMX support. The `parse_map` function still works exactly the same, but will now auto-analyze the file given to it and determine what format it is, and choose the parser accordingly. The same will happen for any tilesets that get loaded during this. Meaning you can load JSON tilesets in a TMX map, and TSX tilesets in a JSON map, with no extra configuration.

The only thing that can't currently be cross-loaded between formats is object templates, if you're using a JSON object template, it will need to be within a JSON map, same for TMX. A `NotImplementedError` will be raised with an appropriate message if you try to cross-load these. Support is planned for this in likely 2.1.0.

The only API change to be worried about here is related to World file loading. Previously in pytiled-parser if you loaded a World file, it would also parse all maps associated with the world. This is not great behavior, as the intention of worlds is to be able to load and unload maps on the fly. With the previous setup, if you had a large world, then every single map would be loaded into memory at startup and is generally not the behavior you'd want if using world files.

To remedy this, the `WorldMap.map_file` attribute has been added to store a `pathlib.Path` to the map file. The previous API had a `WorldMap.tiled_map` attribute which was the fully parsed `pytiled_parser.TiledMap` map object.

## [1.5.4] - 2021-10-12

Previously if only one parallax value(x or y) on a layer had been set, it would fail because pytiled-parser was assuming that if one was set then the other would be. This is not actually the case in the Tiled map file.

The value for them now defaults to 1.0 if it is not specified in the map file(This is the Tiled default value).

## [1.5.3] - 2021-08-28

Just a small bugfix in this release. Previously if a layer's offset was (0, 0), the values for it would not appear in the JSON file, so the `offset` value in the
Layer class would be `None`. This can cause some unexpected behavior in engines or games, and puts the responsibility of checking if this value exists onto the game or engine using it.

This value has been changed to default to (0, 0) if it is not present in the JSON so that games can apply it easily in one line and always get the same result without error.

## [1.5.2] - 2021-07-28

This release contains some re-working to properly support templates.

Previously templates were supposedly fully supported, however they were broken for tile objects. Now there should be out of the box support for auto-loading tile objects from templates. Regardless of where the tileset is defined. See Issue https://github.com/benjamin-kirkbride/pytiled_parser/issues/41 for details

There are no API changes as far as usage is concerned, these were all internal changes to properly support the feature.

This release also contains some minor fixes to docstrings and typing annotations/linting problems.

## [1.5.1] - 2021-07-09

This release contains two bugfixes:

- Pinned minimum attrs version to usage of `kw_only` which was introduced in 18.2.0. See https://github.com/Beefy-Swain/pytiled_parser/pull/39
- Fixed color parsing to be correct. Tiled saves it's colors in either RGB or ARGB format. We were previously parsing RGB correctly, but if an alpha value was present it would be parsed if it were RGBA and so all the values would be offset by one. 

## [1.5.0] - 2021-05-16

This release contains several new features. As of this release pytiled-parser supports 100% of Tiled's feature-set as of Tiled 1.6.

As of version 1.5.0 of pytiled-parser, we are supporting a minimum version of Tiled 1.5. Many features will still work with older versions, but we cannot guarantee functionality with those versions.

### Additions

-   Added support for object template files
-   Added `World` object to support loading Tiled `.world` files.
-   Full support for Wang Sets/Terrains

### Changes

-   The `version` attribute of `TiledMap` and `TileSet` is now a string with Tiled major/minor version. For example `"1.6"`. It used to be a float like `1.6`. This is due to Tiled changing that on their side. pytiled-parser will still load in the value regardless if it is a number or string in the JSON, but it will be converted to a string within pytiled-parser if it comes in as a float.

## [1.4.0] - 2021-04-25

-   Fixes issues with image loading for external tilesets. Previously, if an external tileset was in a different directory than the map file, image paths for the tileset would be incorrect. This was due to all images being given relative paths to the map file, regardless of if they were for an external tileset. This has been solved by giving absolute paths for images from external tilesets. Relative paths for embedded tilesets is still fine as the tileset is part of the map file.

## [1.3.0] - 2021-03-31

-   Added support for Parallax Scroll Factor on Layers. See https://doc.mapeditor.org/en/stable/manual/layers/#parallax-scrolling-factor

-   Added support for Tint Colors on Layers. See https://doc.mapeditor.org/en/stable/manual/layers/#tinting-layers

## [1.2.0] - 2021-02-21

### Changed

-   Made zstd support optional. zstd support can be installed with `pip install pytiled-parser[zstd]`. PyTiled will raise a ValueError explaining to do this if you attempt to use zstd compression without support for it installed. This change is due to the zstd library being a heavy install and a big dependency to make mandatory when most people probably won't ever use it, or can very easily convert to using gzip or zlib for compression.

## [1.1.0] - 2021-02-21

### Added

-   Added support for zstd compression with base64 encoded maps
-   Better project metadata for display on PyPi

## [1.0.0] - 2021-02-21

Initial Project Release
