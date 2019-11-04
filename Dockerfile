#flywheel/fmriprep

############################
# Get the qsiprep algorithm from DockerHub
FROM pennbbl/qsiprep:0.6.4

MAINTAINER Matt Cieslak <matthew.cieslak@pennmedicine.upenn.edu>

ENV QSIPREP_VERSION 0.6.4

############################
# Install basic dependencies
RUN apt-get update && apt-get -y install \
    jq \
    tar \
    zip \
    build-essential


############################
# Install the Flywheel SDK
RUN pip install flywheel-sdk
RUN pip install heudiconv

############################
# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
COPY run ${FLYWHEEL}/run
COPY manifest.json ${FLYWHEEL}/manifest.json

# Set the entrypoint
ENTRYPOINT ["/flywheel/v0/run"]

# Add the fmriprep dockerfile to the container
ADD https://raw.githubusercontent.com/PennBBL/qsiprep/${QSIPREP_VERSION}/Dockerfile ${FLYWHEEL}/qsiprep_${QSIPREP_VERSION}_Dockerfile


############################
# Copy over python scripts that generate the BIDS hierarchy
RUN chmod a+rx ${FLYWHEEL}/*
RUN pip install --upgrade 'fw-heudiconv==0.1.4' ipython


############################
# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

WORKDIR /flywheel/v0
