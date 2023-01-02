#!/bin/bash
set -euo pipefail
mkdir -p build WindTracks SmokeStrobeTracks

while read -r DIR; do
  # Remove "Movies/" from DIR
  MOVIE_NAME="${DIR/Movies\//}"

  echo "$MOVIE_NAME"
  echo "Combining wind/effects tracks..."
  echo

  rm -rf build/*
  # mkdir -p build/"$MOVIE_NAME"

  {
    if [ -f "$DIR"/header.txt ]; then
      cat "$DIR"/header.txt
      echo
    fi
    if [ -f "$DIR"/wind.txt ]; then
      cat "$DIR"/wind.txt
      echo
    fi
    if [ -f "$DIR"/effects.txt ]; then
      echo "// Effects"
      cat "$DIR"/effects.txt
    fi
  } > build/commands.txt

  # cat build/commands.txt
  # echo
  # echo "--------------------------------"
  echo

  rm -f "CombinedTracks/${MOVIE_NAME}.zip"
  (
    cd build
    zip "../CombinedTracks/${MOVIE_NAME}.zip" ./*
  )
done < <(find Movies/* -type d)

# Remove .DS_Store files
find . -name ".DS_Store" -delete
