#!/bin/sh
set -e

cd /usr/src/data

SCRIPTNAME=${1}
shift

python3 /usr/src/scripts/$SCRIPTNAME.py $*
