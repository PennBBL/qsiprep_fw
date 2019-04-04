#!/usr/bin/env sh

set -eu
unset CDPATH
cd "$( dirname "$0" )/../.."

# TODO: export APIKEY

# Define PYTHONPATH
PYTHONPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH

# Run unit tests
RUN_UNIT=true
if ${RUN_UNIT}; then
    printf "INFO: Running unit tests ...\n"
    pytest tests/
fi

