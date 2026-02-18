# GIMI Tools

GIMI = Geospatial-Intelligence (GEOINT) Imagery Media for ISR.

GIMI is a file-format building upon HEIF for storing images, image sequences, and video together with geospatial metadata, stored as RDF in the Turtle format.
This repository contains tools to facilitate converting between GeoTIFF and GIMI files.

You will need a custom compiled `heif-enc` from the `gimi` branch in the [libheif repository](https://github.com/strukturag/libheif.git).
Make sure that `ENABLE_EXPERIMENTAL_FEATURES` is enabled in the cmake configuration.


## Scripts

### geotiff_to_gimi.sh

Converts a GeoTIFF to a GIMI file. This wraps `geotiff_metadata_to_turtle.py` and `heif-enc` into a single command.

```bash
scripts/geotiff_to_gimi.sh <input.tif> [options...] [heif-enc options...]
```

Options handled by the script:

| Option | Description |
|--------|-------------|
| `--tiles` | Output per-tile geospatial coordinates (forwarded to the metadata script) |
| `--ttl NAME` | Save the generated Turtle metadata to NAME instead of a temporary file |
| `--metadata-script FILE` | Use a custom metadata script instead of the built-in `geotiff_metadata_to_turtle.py` |

All other options are forwarded to `heif-enc`.

Examples:

```bash
# Basic conversion
scripts/geotiff_to_gimi.sh image.tif -o output.heif

# With per-tile metadata and heif-enc quality setting
scripts/geotiff_to_gimi.sh image.tif --tiles -q 50 -o output.heif

# Use uncompressed image output
scripts/geotiff_to_gimi.sh image.tif -U -o output.heif

# Keep the Turtle metadata file
scripts/geotiff_to_gimi.sh image.tif --ttl metadata.ttl -o output.heif
```

### geotiff_metadata_to_turtle.py

Extracts geospatial metadata from a GeoTIFF and outputs it as RDF/Turtle to stdout.

```bash
scripts/geotiff_metadata_to_turtle.py <input.tif> [--tiles]
```

Without `--tiles`, outputs a single geometry covering the full image bounds. With `--tiles`, outputs a geometry for each tile in the image's tile grid, including all overview pyramid levels.

**Dependency:** `rasterio` (`pip install rasterio`)
