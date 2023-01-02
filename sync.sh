#!/bin/bash
set -euo pipefail

rsync -rv CombinedTracks/        root@debian-server.local:/opt/HTFanControl/HTFanControl/bin/Debug/net5.0-windows7.0/windtracks/
