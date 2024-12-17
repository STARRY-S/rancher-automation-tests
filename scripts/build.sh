#!/bin/bash

# Build checker cli binary

cd $(dirname $0)/../

set -euo pipefail

go build -o checker .

echo '----------------------'
ls -alh ./checker
echo '----------------------'

echo "Build: Done"
