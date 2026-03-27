#!/bin/bash
set -e

# Temporary build dir for PathMap
TEMP_DIR="/tmp/pathmap_build"
mkdir -p "$TEMP_DIR"

# PathMap repo URL asnd local path
PATHMAP_REPO="https://github.com/Adam-Vandervorst/PathMap.git"
PATHMAP_DIR="$TEMP_DIR/PathMap"

# Clone PathMap outside MORK directory, then build release
if [ ! -d "$PATHMAP_DIR" ]; then
    echo "Cloning PathMap repo outside MORK..."
    git clone "$PATHMAP_REPO" "$PATHMAP_DIR"
fi

cd "$PATHMAP_DIR"
echo "Building PathMap release..."
cargo build --release
cd -

# Now build MORK (server branch)
MORK_REPO="https://github.com/rejuve-bio/MORK.git"
MORK_DIR="/app/MORK"

git checkout -f server
ls
cd "./server"
echo "Building MORK server release..."
cargo build --release

echo "Running MORK server..."
../target/release/mork_server