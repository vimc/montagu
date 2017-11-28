#!/usr/bin/env bash
SCRIPT=$0
MONTAGU_PATH=$(git -C $(dirname $SCRIPT) rev-parse --show-toplevel)

## NOTE: this is *not* Rich's email but one associated with our robot
## account https://github.com/vimc-robot
git -C $MONTAGU_PATH config user.email "rich.fitzjohn+vimc@gmail.com"
git -C $MONTAGU_PATH config user.name "vimc-robot"
