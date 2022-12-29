#!/bin/bash
set -euo pipefail
ssh root@debian-server "systemctl restart HTFanControlSmokeStrobe.service"
ssh root@debian-server "systemctl restart HTFanControl.service"
