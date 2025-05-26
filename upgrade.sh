#!/bin/bash

set -euo pipefail

git add -A
git commit -m "autocommit"
git push
uv tool upgrade filter
