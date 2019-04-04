
## Phasediff EchoTime1, EchoTime2

Section 8.3.5.1 of the BIDS Spec indicates that the phasediff sidecar should include EchoTime1 and EchoTime2, which correspond
to the echo times on the magnitude 1 and 2 images. 

In order to initialize the values via template, we can create the following resolver rules, which will use 
the EchoTime1 and EchoTime2 filters to initialize the EchoTime values:
```json
"resolvers": [
{
	"id": "phasediff_echo_time1",
	"templates": ["fieldmap_file"],
	"update": "file.info.EchoTime1",
	"filter": "file.info.BIDS.EchoTime1",
	"resolveFor": "session",
	"type": "file",
	"value": "file.info.EchoTime"
},
{
	"id": "phasediff_echo_time2",
	"templates": ["fieldmap_file"],
	"update": "file.info.EchoTime2",
	"filter": "file.info.BIDS.EchoTime2",
	"resolveFor": "session",
	"type": "file",
	"value": "file.info.EchoTime"
}
]
```

Then, in the Rule where you set the phasediff modality, you should initialize the EchoTime1, and EchoTime2 filters as follows:

```json
{
  "rule": "phasediff_fieldmap_file",
  "where": {
	"file.info.ImageType": "P"
  },
  "initialize": {
	"Modality": "phasediff",
	"EchoTime1": [{
		"Folder": "fmap",
		"Modality": "magnitude1"
	}],
	"EchoTime2": [{
		"Folder": "fmap",
		"Modality": "magnitude2"
	}],
	"delete_info": [ "EchoTime", "EchoNumber" ]
  }
}
```

Note that we also use `delete_info` to specify to exclude the original `EchoTime` and `EchoNumber` fields from the exported sidecar.

