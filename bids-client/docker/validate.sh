#!/bin/bash
if [ -d "$1" ]; then
	BIDS_DIR=`realpath $1`
	echo "Using bids dir: ${BIDS_DIR}"
	shift
else
	echo "Usage: $0 <bids-dir> [options...]"
	exit 1
fi

docker build -t flywheel/bids-client .
docker run -it --rm	-v ${BIDS_DIR}:/local/bids \
	flywheel/bids-client \
	/usr/bin/bids-validator /local/bids


