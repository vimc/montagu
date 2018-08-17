#!/usr/bin/env bash
set -e
SCRIPT=$0
MONTAGU_PATH=$(git -C $(dirname $SCRIPT) rev-parse --show-toplevel)

## NOTE: this is *not* Rich's email but one associated with our robot
## account https://github.com/vimc-robot
echo "Setting git username and password for $MONTAGU_PATH"
git -C $MONTAGU_PATH config user.email "rich.fitzjohn+vimc@gmail.com"
git -C $MONTAGU_PATH config user.name "vimc-robot"
echo "Done"
