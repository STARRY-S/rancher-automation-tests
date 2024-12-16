#!/bin/bash

cd $(dirname $0)/../

set -euo pipefail

go build -o checker .
