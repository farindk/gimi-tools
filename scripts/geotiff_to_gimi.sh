#!/usr/bin/env bash
#
# Convert a GeoTIFF to GIMI format.
#
# Usage: geotiff_to_gimi.sh <input.tif> [--ttl out.ttl] [--tiles] [heif-enc options...]
#
# Options handled by this script:
#   --ttl NAME              Save the Turtle metadata to NAME (otherwise uses a temp file)
#   --metadata-script FILE  Use FILE instead of geotiff_metadata_to_turtle.py
#
# Options forwarded to geotiff_metadata_to_turtle.py:
#   --tiles              Output per-tile coordinates
#
# All other options are forwarded to heif-enc.
#
# Copyright (C) 2026 dirk.farin@gmail.com
# SPDX-License-Identifier: GPL-3.0-or-later

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
    echo "Usage: $0 <input.tif> [--ttl out.ttl] [--tiles] [heif-enc options...]"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

INPUT_FILE="$1"
shift

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: file not found: $INPUT_FILE" >&2
    exit 1
fi

# Separate arguments: --tiles goes to the Python script,
# everything else goes to heif-enc.
PYTHON_ARGS=()
HEIF_ARGS=()
TTL_OUTPUT=""
METADATA_SCRIPT="$SCRIPT_DIR/geotiff_metadata_to_turtle.py"

while [ $# -gt 0 ]; do
    case "$1" in
        --ttl)
            if [ $# -lt 2 ]; then
                echo "Error: --ttl requires an argument" >&2
                exit 1
            fi
            TTL_OUTPUT="$2"
            shift 2
            ;;
        --metadata-script)
            if [ $# -lt 2 ]; then
                echo "Error: --metadata-script requires an argument" >&2
                exit 1
            fi
            METADATA_SCRIPT="$2"
            shift 2
            ;;
        --tiles)
            PYTHON_ARGS+=("$1")
            shift
            ;;
        *)
            HEIF_ARGS+=("$1")
            shift
            ;;
    esac
done

if [ -n "$TTL_OUTPUT" ]; then
    TURTLE_FILE="$TTL_OUTPUT"
else
    TURTLE_FILE="$(mktemp "${TMPDIR:-/tmp}/gimi-XXXXXX.ttl")"
    trap 'rm -f "$TURTLE_FILE"' EXIT
fi

# Step 1: Extract RDF/Turtle metadata from the GeoTIFF.
python3 "$METADATA_SCRIPT" "$INPUT_FILE" \
    ${PYTHON_ARGS[@]+"${PYTHON_ARGS[@]}"} > "$TURTLE_FILE"

# Step 2: Encode the image as GIMI with the metadata.
heif-enc "$INPUT_FILE" --turtle "$TURTLE_FILE" ${HEIF_ARGS[@]+"${HEIF_ARGS[@]}"}
