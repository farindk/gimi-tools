#!/usr/bin/env python3
#
# Convert GeoTIFF metadata to RDF/Turtle format.
#
# Copyright (C) 2026 dirk.farin@gmail.com
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import uuid
import argparse
import rasterio
from rasterio.windows import Window, bounds as window_bounds
from rasterio.warp import transform_bounds
from rasterio.transform import Affine


PREFIX_BLOCK = """@prefix cco: <https://www.commoncoreontologies.org/> .
@prefix geosparql: <http://www.opengis.net/ont/geosparql#> .
@prefix imh: <http://ontology.mil/foundry/IMH_> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""


def reproject_bounds(src_crs, left, bottom, right, top):
    if src_crs is None:
        raise ValueError("GeoTIFF has no CRS defined.")

    if src_crs.to_epsg() == 4326:
        return left, bottom, right, top
    return transform_bounds(src_crs, "EPSG:4326",
                            left, bottom, right, top)


def bounds_to_wkt(minx, miny, maxx, maxy):
    return (
        f"POLYGON(("
        f"{maxx} {maxy},"
        f"{maxx} {miny},"
        f"{minx} {miny},"
        f"{minx} {maxy},"
        f"{maxx} {maxy}"
        f"))"
    )


def emit_geometry(image_uuid, src_crs, label, left, bottom, right, top):
    minx, miny, maxx, maxy = reproject_bounds(src_crs, left, bottom, right, top)
    wkt = bounds_to_wkt(minx, miny, maxx, maxy)
    geom_uuid = uuid.uuid4()
    return (
        f"# {label}\n"
        f"<urn:uuid:{geom_uuid}> a geosparql:Geometry ;\n"
        f'    geosparql:asWKT "{wkt}"^^geosparql:wktLiteral ;\n'
        f"    cco:ont00001808 <urn:uuid:{image_uuid}> .\n"
    )


def emit_tiles(src, image_uuid, overview_level):
    if overview_level == 0:
        transform = src.transform
        width = src.width
        height = src.height
    else:
        factor = src.overviews(1)[overview_level - 1]
        transform = src.transform * Affine.scale(factor)
        width = src.width // factor
        height = src.height // factor

    blockx, blocky = src.block_shapes[0]

    tiles_x = (width + blockx - 1) // blockx
    tiles_y = (height + blocky - 1) // blocky

    output = []

    for ty in range(tiles_y):
        for tx in range(tiles_x):

            col = tx * blockx
            row = ty * blocky

            w = Window(
                col,
                row,
                min(blockx, width - col),
                min(blocky, height - row)
            )

            left, bottom, right, top = window_bounds(w, transform)

            output.append(emit_geometry(
                image_uuid, src.crs,
                f"tile {overview_level} {tx} {ty}",
                left, bottom, right, top))

    return "\n".join(output)


def emit_image_bounds(src, image_uuid):
    left, bottom, right, top = window_bounds(
        Window(0, 0, src.width, src.height), src.transform)
    minx, miny, maxx, maxy = reproject_bounds(
        src.crs, left, bottom, right, top)
    wkt = bounds_to_wkt(minx, miny, maxx, maxy)
    geom_uuid = uuid.uuid4()
    return (
        f"<urn:uuid:{geom_uuid}> a geosparql:Geometry ;\n"
        f'    geosparql:asWKT "{wkt}"^^geosparql:wktLiteral ;\n'
        f"    cco:ont00001808 <urn:uuid:{image_uuid}> .\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input GeoTIFF")
    parser.add_argument("--tiles", action="store_true",
                        help="Output per-tile coordinates instead of full image")
    args = parser.parse_args()

    image_uuid = uuid.uuid4()

    print(PREFIX_BLOCK)

    # Image header
    print("# image")
    print(f"<urn:uuid:{image_uuid}> a cco:ont00002004 .\n")

    try:
        src = rasterio.open(args.input)
    except Exception as e:
        print(f"Error: Could not open '{args.input}': {e}", file=sys.stderr)
        sys.exit(1)

    with src:
        if args.tiles:
            print(emit_tiles(src, image_uuid, 0))
            for i in range(len(src.overviews(1))):
                print(emit_tiles(src, image_uuid, i + 1))
        else:
            print(emit_image_bounds(src, image_uuid))


if __name__ == "__main__":
    main()
