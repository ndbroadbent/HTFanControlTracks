#!/bin/bash
set -euo pipefail
mkdir -p build WindTracks SmokeStrobeTracks

while read -r DIR; do
  # Remove "Movies/" from DIR
  MOVIE_NAME="${DIR/Movies\//}"

  echo "$MOVIE_NAME"

  rm -rf build/*
  # mkdir -p build/"$MOVIE_NAME"
  cp "$DIR"/wind_commands.txt build/commands.txt
  rm -f "WindTracks/${MOVIE_NAME}.zip"
  (
    cd build
    zip "../WindTracks/${MOVIE_NAME}.zip" ./*
  )

  rm -rf build/*
  # mkdir -p build/"$MOVIE_NAME"
  echo "Converting smoke/strobe track..."

  sed -e "s/,SMOKE_ON/,ECO/g" \
      -e "s/,SMOKE_OFF/,OFF/g" \
      -e "s/,STROBE_FLASH/,LOW/g" \
    "$DIR"/smoke_strobe_commands.txt > build/commands.txt

  #cat build/commands.txt
  rm -f "SmokeStrobeTracks/${MOVIE_NAME}.zip"
  (
    cd build
    zip "../SmokeStrobeTracks/${MOVIE_NAME}.zip" ./*
  )

done < <(find Movies/* -type d)
