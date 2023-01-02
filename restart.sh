#!/bin/bash
set -euo pipefail
ssh root@debian-server "systemctl restart HTFanControl"
