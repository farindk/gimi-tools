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
| `--ttl NAME` | Save the generated Turtle metadata to NAME instead of embedding it in the HEIF |
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

# Keep the Turtle metadata file, do not embed it in the HEIF
scripts/geotiff_to_gimi.sh image.tif --ttl metadata.ttl -o output.heif
```

### geotiff_metadata_to_turtle.py

Extracts geospatial metadata from a GeoTIFF and outputs it as RDF/Turtle to stdout.

```bash
scripts/geotiff_metadata_to_turtle.py <input.tif> [--tiles]
```

Without `--tiles`, outputs a single geometry covering the full image bounds. With `--tiles`, outputs a geometry for each tile in the image's tile grid, including all overview pyramid levels.

**Dependency:** `rasterio` (`pip install rasterio`)


### Turtle Metadata to `heif-enc` interop

When writing the metadata, `heif-enc` expects certain comments added to know from where to extract the content-IDs for the image and the tiles.
The comments should be placed in the Turtle file like this:
````
@prefix cco: <https://www.commoncoreontologies.org/> .
@prefix geosparql: <http://www.opengis.net/ont/geosparql#> .
@prefix imh: <http://ontology.mil/foundry/IMH_> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .


# image
<urn:uuid:cc7fa21b-cc07-41ca-a6de-818c1b6e97dd> a cco:ont00002004 .

# tile 0 0 0
<urn:uuid:aa175789-c516-4b8e-bf5d-0e65148dab11> a geosparql:Geometry ;
    geosparql:asWKT "POLYGON((-74.37247488057636 40.5655827442333,-74.37247488057636 40.560937758633564,-74.37856552044943 40.560937758633564,-74.37856552044943 40.5655827442333,-74.37247488057636 40.5655827442333))"^^geosparql:wktLiteral ;
    cco:ont00001808 <urn:uuid:cc7fa21b-cc07-41ca-a6de-818c1b6e97dd> .

# tile 0 1 0
<urn:uuid:b98ea43b-d60b-44f5-9aa3-d29c8d81843d> a geosparql:Geometry ;
    geosparql:asWKT "POLYGON((-74.36642690921177 40.56555005005991,-74.36642690921177 40.560904753211666,-74.37251795419041 40.560904753211666,-74.37251795419041 40.56555005005991,-74.36642690921177 40.56555005005991))"^^geosparql:wktLiteral ;
    cco:ont00001808 <urn:uuid:cc7fa21b-cc07-41ca-a6de-818c1b6e97dd> .
````

The comment `# image` denotes the main image. `heif-enc` will read the content-ID from the following line and assign it to the image.
The comment `# tile L X Y` denotes an image tile. `L` is the overview layer (0 = highest resolution), `X` and `Y` are the tile position.
