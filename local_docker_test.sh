docker run --rm -ti \
  --entrypoint=/bin/bash \
  -v /Users/mcieslak/projects/upenn/flywheel/qsiprep_fw_debug/qsiprep-fw-0_5caa3026f546b6002cef9de3/input:/flywheel/v0/input \
  -v /Users/mcieslak/projects/upenn/flywheel/qsiprep_fw_debug/qsiprep-fw-0_5caa3026f546b6002cef9de3/output:/flywheel/v0/output \
  -v /Users/mcieslak/projects/upenn/flywheel/qsiprep_fw_debug/qsiprep-fw-0_5caa3026f546b6002cef9de3/config.json:/flywheel/v0/config.json \
  pennbbl/qsiprep-fw:0.1.5_0.2.3
