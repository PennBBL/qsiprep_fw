#flywheel/fmriprep

############################
# Get the fmriprep algorithm from DockerHub
FROM pennbbl/qsiprep:0.2.0

MAINTAINER Matt Cieslak <matthew.cieslak@pennmedicine.upenn.edu>

ENV QSIPREP_VERSION 0.2.0

############################
# Install basic dependencies
RUN apt-get update && apt-get -y install \
    jq \
    tar \
    zip \
    build-essential


############################
# Install the Flywheel SDK
RUN pip install 'flywheel-sdk==4.4.4'

############################
# Install the Flywheel BIDS client
COPY bids-client /bids-client
RUN cd /bids-client \
    && pip install -e .[all]

############################
# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
COPY run ${FLYWHEEL}/run
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY fs_license.py /flywheel/v0/fs_license.py

# Set the entrypoint
ENTRYPOINT ["/flywheel/v0/run"]

# Add the fmriprep dockerfile to the container
ADD https://raw.githubusercontent.com/pennbbl/qsiprep/${QSIIPREP_VERSION}/Dockerfile ${FLYWHEEL}/qsiprep_${QSIPREP_VERSION}_Dockerfile


############################
# Copy over python scripts that generate the BIDS hierarchy
COPY create_archive.py /flywheel/v0/create_archive.py
COPY create_archive_funcs.py /flywheel/v0/create_archive_funcs.py
RUN chmod +x ${FLYWHEEL}/*


############################
# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

WORKDIR /flywheel/v0
