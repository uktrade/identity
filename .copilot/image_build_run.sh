#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

echo "Running post build script"
export $(grep -v '^#' .env.ci | xargs)