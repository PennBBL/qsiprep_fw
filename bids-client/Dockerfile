# bids-uploader
#
# Upload BIDS dataset
#
# Example usage:
# docker run --rm -it \
#    -v  /path/to/bids/directory:/bids_dir \
#    bids-uploader /bin/bash


FROM python:2.7-alpine3.7
MAINTAINER Flywheel <support@flywheel.io>

RUN apk add --no-cache nodejs bash

RUN npm install -g bids-validator@0.25.14

# Install jsonschema
COPY requirements.txt /var/flywheel/code/requirements.txt
RUN pip install -qq -r /var/flywheel/code/requirements.txt

COPY . /var/flywheel/code/bids-client
RUN pip install --no-deps /var/flywheel/code/bids-client

