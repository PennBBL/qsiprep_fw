#!/bin/bash
docker build -t flywheel/bids-client .
docker run -it --rm --net host flywheel/bids-client \
	curate_bids "$@"

