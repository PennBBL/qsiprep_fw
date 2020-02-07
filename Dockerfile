#flywheel/fmriprep

############################
# Get the qsiprep algorithm from DockerHub
FROM pennbbl/qsiprep:0.7.2

MAINTAINER Matt Cieslak <matthew.cieslak@pennmedicine.upenn.edu>

ENV QSIPREP_VERSION 0.7.2

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
RUN pip install --upgrade fw-heudiconv ipython


############################
# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
# Add the qsiprep dockerfile to the container
ADD https://raw.githubusercontent.com/PennBBL/qsiprep/${QSIPREP_VERSION}/Dockerfile ${FLYWHEEL}/qsiprep_${QSIPREP_VERSION}_Dockerfile
RUN mkdir -p ${FLYWHEEL}
COPY run ${FLYWHEEL}/run
COPY prepare_run.py ${FLYWHEEL}/prepare_run.py
COPY move_to_project.py ${FLYWHEEL}/move_to_project.py
COPY manifest.json ${FLYWHEEL}/manifest.json
RUN chmod a+rx ${FLYWHEEL}/*

# Set the entrypoint
ENTRYPOINT ["/flywheel/v0/run"]

############################
# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

WORKDIR /flywheel/v0
