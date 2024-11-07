#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

echo "Running post build script"

echo "Renaming .env.ci to .env"
mv ".env.ci" ".env"

cd src

echo "Renaming .env to .env.ci"
cd ../
mv ".env" ".env.ci"