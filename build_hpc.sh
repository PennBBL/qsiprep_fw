# After merging master, run this script to build and upload the hpc-version
sed -i 's/qsiprep-fw\([^-]\)/qsiprep-fw-hpc\1/g' manifest.json
IMAGENAME=$(cat manifest.json | grep \"image\": | sed 's/^.*"image": "\(.*\)".*/\1/')
docker build -t ${IMAGENAME} .
docker push ${IMAGENAME}
