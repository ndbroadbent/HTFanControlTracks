#!/bin/bash
set -euo pipefail
./compile.sh
./sync.sh
./restart.sh
