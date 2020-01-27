docker run --rm -ti \
    --entrypoint=/bin/bash \
    -v /home/mcieslak/projects/07test/qsiprep-fw-0.3.14_0.7.0_5e2f05af86b137032c292141/input:/flywheel/v0/input \
    -v /home/mcieslak/projects/07test/qsiprep-fw-0.3.14_0.7.0_5e2f05af86b137032c292141/output:/flywheel/v0/output \
    -v /home/mcieslak/projects/07test/qsiprep-fw-0.3.14_0.7.0_5e2f05af86b137032c292141/config.json:/flywheel/v0/config.json \
    pennbbl/qsiprep-fw:0.3.14_0.7.0
