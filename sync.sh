#!/bin/bash
set -euo pipefail

rsync -rv WindTracks/        root@debian-server.local:/opt/HTFanControl/windtracks
rsync -rv SmokeStrobeTracks/ root@debian-server.local:/opt/HTFanControlSmokeStrobe/windtracks
