#!/bin/bash
set -euo pipefail
./compile.sh
./sync.sh
ssh root@debian-server "systemctl restart HTFanControlSmokeStrobe.service"
ssh root@debian-server "systemctl restart HTFanControl.service"
