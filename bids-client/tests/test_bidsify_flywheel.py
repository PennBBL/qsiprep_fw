import os
import json
import re
import shutil
import unittest

from flywheel_bids.supporting_files import utils, bidsify_flywheel

class BidsifyTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'
        self.maxDiff = None

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def test_process_string_template_required(self):
        """  """
        # Define project template from the templates file
        auto_update_str = 'sub-<subject.code>_ses-<session.label>_bold.nii.gz'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': u'00123'},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = utils.process_string_template(auto_update_str, context)

        self.assertEqual(updated_string,
                'sub-%s_ses-%s_bold.nii.gz' % (
                    context['subject']['code'],
                    context['session']['label'],
                    ))

    def test_process_string_template_bids1(self):
        """  """
        # Get project template from the templates file
        auto_update_str = 'sub-<subject.code>_ses-<session.label>_bold.nii.gz'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': u'sub-01'},
            'session': {u'label': u'ses-001'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = utils.process_string_template(auto_update_str, context)

        self.assertEqual(updated_string,
                '%s_%s_bold.nii.gz' % (
                    context['subject']['code'],
                    context['session']['label']
                    ))

    def test_process_string_template_optional(self):
        """  """
        # Define string to auto update, subject code is optional
        auto_update_str = '[sub-<subject.code>]_ses-<session.label>_acq-<acquisition.label>_bold.nii.gz'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': None},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = utils.process_string_template(auto_update_str, context)
        # Assert function honors the optional 'sub-<subject.code>'
        self.assertEqual(updated_string,
                '_ses-%s_acq-%s_bold.nii.gz' % (
                    context['session']['label'],
                    context['acquisition']['label']
                    ))

    def test_process_string_template_full_optional(self):
        """ """
        auto_update_str = 'sub-<subject.code>[_ses-<session.label>][_acq-{file.info.BIDS.Acq}][_ce-{file.info.BIDS.Ce}][_rec-{file.info.BIDS.Rec}][_run-{file.info.BIDS.Run}][_mod-{file.info.BIDS.Mod}]'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': u'123'},
            'session': {u'label': u'456'},
            'acquisition': {u'label': u'acq222'},
            'file': {u'classification': {u'Measurement': u'T1', u'Intent': u'Structural'}},
            'ext': '.nii.gz'
        }

        # Call function
        updated_string = utils.process_string_template(auto_update_str, context)
        # Assert function honors the optional labels
        self.assertEqual(updated_string,
                'sub-123_ses-456')

    def test_process_string_template_func_filename1(self):
        """  """
        # Define string to auto update, subject code is optional
        auto_update_str = 'sub-<subject.code>[_ses-<session.label>]_task-{file.info.BIDS.Task}_bold{ext}'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': '001'},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': {'name': 'bold.nii.gz',
                'info': {'BIDS': {'Task': 'test123', 'Modality': 'bold'}}},
            'ext': '.nii.gz'
        }

        # Call function
        updated_string = utils.process_string_template(auto_update_str, context)
        # Assert string as expected
        self.assertEqual(updated_string,
                'sub-%s_ses-%s_task-%s_%s%s' % (
                    context['subject']['code'],
                    context['session']['label'],
                    context['file']['info']['BIDS']['Task'],
                    context['file']['info']['BIDS']['Modality'],
                    context['ext']
                    ))

    def test_process_string_template_required_notpresent(self):
        """ """
        # TODO: Determine the expected behavior of this...
        # Define string to auto update
        auto_update_str = 'sub-<subject.code>_ses-<session.label>'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = utils.process_string_template(auto_update_str, context)
        # Assert function honors the optional 'sub-<subject.code>'
        self.assertEqual(updated_string,
                'sub-<subject.code>_ses-%s' % (
                    context['session']['label']
                    ))

    def test_process_string_template_required_None(self):
        """ """
        # TODO: Determine the expected behavior of this...
        # Define string to auto update
        auto_update_str = 'sub-<subject.code>_ses-<session.label>'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': None},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = utils.process_string_template(auto_update_str, context)
        # Assert function honors the optional 'sub-<subject.code>'
        self.assertEqual(updated_string,
                'sub-<subject.code>_ses-%s' % (
                    context['session']['label']
                    ))

    def test_add_properties_valid(self):
        """ """
        properties = {
                "Filename": {"type": "string", "label": "Filename", "default": "",
                    "auto_update": 'sub-<subject.code>_ses-<session.label>[_acq-<acquisition.label>]_T1w{ext}'},
                "Folder": {"type": "string", "label":"Folder", "default": "anat"},
                "Ce": {"type": "string", "label": "CE Label", "default": ""},
                "Rec": {"type": "string", "label": "Rec Label", "default": ""},
                "Run": {"type": "string", "label": "Run Index", "default": ""},
                "Mod": {"type": "string", "label": "Mod Label", "default": ""},
                "Modality": {"type": "string", "label": "Modality Label", "default": "T1w",
                    "enum": [
                        "T1w","T2w","T1rho","T1map","T2map","FLAIR","FLASH","PD","PDmap",
                        "PDT2","inplaneT1","inplaneT2","angio","defacemask","SWImagandphase"
                        ]
                    }
                }
        project_obj = {u'label': u'Project Name'}
        # Call function
        info_obj = bidsify_flywheel.add_properties(properties, project_obj, [u'anatomy_t1w'])
        # Expected info object
        for key in properties:
            project_obj[key] = properties[key]['default']
        self.assertEqual(info_obj, project_obj)

    def test_update_properties_valid(self):
        """ """
        # Define inputs
        properties = {
            "Filename": {"type": "string", "label": "Filename", "default": "",
                "auto_update": 'sub-<subject.code>_ses-<session.label>[_acq-<acquisition.label>]_T1w{ext}'},
            "Folder": {"type": "string", "label":"Folder", "default": "anat"},
            "Mod": {"type": "string", "label": "Mod Label", "default": ""},
            "Modality": {"type": "string", "label": "Modality Label", "default": "T1w"}
        }
        context = {
            'container_type': 'file', 'parent_container_type': 'acquisition',
            'project': None, 'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'}, 'acquisition': {u'label': u'acqTEST'},
            'file': {
                u'classification': {u'Measurement': u'T1', u'Intent': u'Structural'},
                u'type': u'nifti'
            },
            'ext': '.nii.gz'
        }
        project_obj = {u'test1': u'123', u'test2': u'456'}
        # Call function
        info_obj = bidsify_flywheel.update_properties(properties, context, project_obj)
        # Update project_obj, as expected
        project_obj['Filename'] = u'sub-%s_ses-%s_acq-%s_T1w%s' % (
                context['subject']['code'],
                context['session']['label'],
                context['acquisition']['label'],
                context['ext']
                )
        self.assertEqual(project_obj, info_obj)

    def test_process_matching_templates_anat_t1w(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Measurement': u'T1', u'Intent': u'Structural'},
                    u'type': u'nifti'
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'anat_file',
                    'Filename': u'sub-001_ses-sesTEST_T1w.nii.gz',
                    'Path': u'sub-001/ses-sesTEST/anat', 'Folder': 'anat',
                    'Run': '', 'Acq': '', 'Ce': '', 'Rec': '',
                    'Modality': 'T1w', 'Mod': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Measurement': u'T1', u'Intent': u'Structural'}, u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_anat_t2w(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Measurement': u'T2', u'Intent': u'Structural'},
                    u'type': u'nifti'
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'anat_file',
                    'Filename': u'sub-001_ses-sesTEST_T2w.nii.gz',
                    'Path': u'sub-001/ses-sesTEST/anat', 'Folder': 'anat',
                    'Run': '', 'Acq': '', 'Ce': '', 'Rec': '',
                    'Modality': 'T2w', 'Mod': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Measurement': u'T2', u'Intent': u'Structural'}, u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_func(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'run_counters': utils.RunCounterMap(),
            'acquisition': {u'label': u'acq_task-TEST_run+'},
            'file': {u'classification': {u'Intent': u'Functional'},
                    u'type': u'nifti',
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'func_file',
                    'Filename': u'sub-001_ses-sesTEST_task-TEST_run-1_bold.nii.gz',
                    'Folder': 'func', 'Path': u'sub-001/ses-sesTEST/func',
                    'Acq': '', 'Task': 'TEST', 'Modality': 'bold',
                    'Rec': '', 'Run': '1', 'Echo': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Intent': u'Functional'}, u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_task_events(self):
        """"""
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Intent': u'Functional'},
                    u'type': u'tabular data',
                        },
            'ext': '.tsv'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'task_events_file',
                    'Filename': u'sub-001_ses-sesTEST_task-{file.info.BIDS.Task}_events.tsv',
                    'Folder': 'func', 'Path': u'sub-001/ses-sesTEST/func',
                    'Acq': '', 'Task': '',
                    'Rec': '', 'Run': '', 'Echo': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Intent': u'Functional'}, u'type': u'tabular data'}
        self.assertEqual(container, container_expected)

    def test_process_matching_beh_events_file(self):
        """"""
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Custom': u'Behavioral'},
                    u'type': u'tabular data',
                        },
            'ext': '.tsv'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'beh_events_file',
                    'Filename': u'sub-001_ses-sesTEST_task-{file.info.BIDS.Task}_events.tsv',
                    'Folder': 'beh', 'Path': u'sub-001/ses-sesTEST/beh', 'Task': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Custom': u'Behavioral'}, u'type': u'tabular data'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_physio_task_events(self):
        """"""
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Custom': u'Physio'},
                    u'type': u'tabular data',
                        },
            'ext': '.tsv'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'physio_task_file',
                    'Filename': u'sub-001_ses-sesTEST_task-{file.info.BIDS.Task}_physio.tsv',
                    'Folder': 'func', 'Path': u'sub-001/ses-sesTEST/func',
                    'Acq': '', 'Task': '',
                    'Modality': 'physio',
                    'Rec': '',
                    'Recording': '',
                    'Run': '',
                    'Echo': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Custom': u'Physio'}, u'type': u'tabular data'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dwi_nifti(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'},
                    u'type': u'nifti'
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'diffusion_file',
                    'Filename': u'sub-001_ses-sesTEST_dwi.nii.gz',
                    'Path': u'sub-001/ses-sesTEST/dwi', 'Folder': 'dwi',
                     'Modality': 'dwi', 'Acq': '', 'Run': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'}, u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dwi_bval(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'},
                    u'type': u'bval'
                        },
            'ext': '.bval'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'diffusion_file',
                    'Filename': u'sub-001_ses-sesTEST_dwi.bval',
                    'Path': u'sub-001/ses-sesTEST/dwi', 'Folder': 'dwi',
                     'Modality': 'dwi', 'Acq': '', 'Run': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'}, u'type': u'bval'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dwi_bvec(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'},
                    u'type': u'bvec'
                        },
            'ext': '.bvec'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'diffusion_file',
                    'Filename': u'sub-001_ses-sesTEST_dwi.bvec',
                    'Path': u'sub-001/ses-sesTEST/dwi', 'Folder': 'dwi',
                     'Modality': 'dwi', 'Acq': '', 'Run': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'}, u'type': u'bvec'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_fieldmap(self):
        """"""
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'classification': {u'Intent': u'Fieldmap'},
                    u'type': u'nifti',
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'fieldmap_file',
                    'Filename': u'sub-001_ses-sesTEST_fieldmap.nii.gz',
                    'Folder': 'fmap', 'Path': u'sub-001/ses-sesTEST/fmap',
                    'Acq': '', 'Run': '', 'Dir': '', 'Modality': 'fieldmap',
                    'IntendedFor': [
                        {'Folder': 'anat'},
                        {'Folder': 'func'}
                    ],
                    'ignore': False
                    }
                },
            u'classification': {u'Intent': u'Fieldmap'}, u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_fieldmap_phase_encoded(self):
        """"""
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST Topup PA'}, # Acquisition label needs to contain
            'file': {u'classification': {u'Intent': u'Fieldmap'},
                    u'type': u'nifti'
                    },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'fieldmap_phase_encoded_file',
                    'Filename': u'sub-001_ses-sesTEST_dir-PA_epi.nii.gz',
                    'Folder': 'fmap', 'Path': u'sub-001/ses-sesTEST/fmap',
                    'Acq': '', 'Run': '', 'Dir': 'PA', 'Modality': 'epi',
                    'IntendedFor': [
                        {'Folder': 'anat'},
                        {'Folder': 'func'}
                    ],
                    'ignore': False
                    }
                },
            u'classification': {u'Intent': u'Fieldmap'}, u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dicom(self):
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': {u'label': 'hello'},
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {
                u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'},
                u'type': u'dicom'
            },
            'ext': '.dcm.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {'info': {'BIDS': {
                'template': 'dicom_file',
                'Filename': '',
                'Folder': 'sourcedata',
                'Path': u'sourcedata/sub-001/ses-sesTEST',
                'ignore': False
                }},
            u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'},
            u'type': u'dicom'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_non_bids_dicom(self):
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': {u'label': 'hello'},
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST', u'id': u'09090'},
            'file': {
                u'name': u'4784_1_1_localizer',
                u'classification': {u'Measurement': u'T2', u'Intent': u'Localizer'},
                u'type': u'dicom'
            },
            'ext': '.dcm.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        print(container)
        # Define expected container
        container_expected = {
            u'name': u'4784_1_1_localizer',
            u'classification': {u'Measurement': u'T2', u'Intent': u'Localizer'},
            u'type': u'dicom'
        }
        self.assertEqual(container, container_expected)

    def test_resolve_initial_dicom_field_values_from_filename(self):
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': {u'label': 'hello'},
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {
                u'name': u'09 cmrr_mbepi_task-spatialfrequency_s6_2mm_66sl_PA_TR1.0.dcm.zip',
                u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'},
                u'type': u'dicom'
            },
            'ext': '.dcm.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {'info': {'BIDS': {
                'template': 'dicom_file',
                'Filename': u'09 cmrr_mbepi_task-spatialfrequency_s6_2mm_66sl_PA_TR1.0.dcm.zip',
                'Folder': 'sourcedata',
                'Path': u'sourcedata/sub-001/ses-sesTEST',
                'ignore': False
                }},
            u'name': u'09 cmrr_mbepi_task-spatialfrequency_s6_2mm_66sl_PA_TR1.0.dcm.zip',
            u'classification': {u'Measurement': u'Diffusion', u'Intent': u'Structural'},
            u'type': u'dicom'}
        self.assertEqual(container, container_expected)

    def test_process_matching_template_acquisition(self):
        """ """
        # Define context
        context = {
            'container_type': 'acquisition',
            'parent_container_type': 'session',
            'project': {'label': 'Project_Label_Test'},
            'subject': None,
            'session': {'label': 'Session_Label_Test'},
            'acquisition': {'label': 'Acquisition_Label_Test'},
            'file': {},
            'ext': '.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'acquisition',
                    'ignore': False
                    }
                },
                'label': 'Acquisition_Label_Test'
            }
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_acquisition_file(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': {'label': 'testproject'},
            'subject': {'code': '12345'},
            'session': {'label': 'haha', 'info': {'BIDS': {'Label': 'haha', 'Subject': '12345'}}},
            'acquisition':{'label': 'blue', u'id': u'ID'},
            'file': {u'type': u'image', u'name': u'fname'},
            'ext': '.jpg'
        }
        # Won't match if not on upload
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {u'type': u'image', u'name': u'fname'}
        self.assertEqual(container, container_expected)
        # Call function
        container = bidsify_flywheel.process_matching_templates(context, upload=True)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'acquisition_file',
                    'Filename': '', 'Folder': 'acq-blue', 'Path': 'sub-12345/ses-haha/acq-blue',
                    'ignore': False
                    }
                },
            u'type': u'image',
            u'name': u'fname'
            }
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_session(self):
        """ """
        # Define context
        context = {
            'container_type': 'session',
            'parent_container_type': 'project',
            'project': {'label': 'Project_Label_Test'},
            'subject': {'code' : '12345'},
            'session': {'label': 'Session_Label_Test'},
            'acquisition': None,
            'file': {},
            'ext': '.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Label': 'SessionLabelTest',
                    'Subject': '12345',
                    'template': 'session',
                    'ignore': False
                    }
                },
                'label': 'Session_Label_Test'
            }
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_session_file(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'session',
            'project': {'label': 'testproject'},
            'subject': {'code': '12345'},
            'session': {'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'12345'}}},
            'acquisition': None,
            'file': {u'type': u'tabular'},
            'ext': '.tsv'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'session_file',
                    'Filename': '', 'Folder': 'ses-sesTEST', 'Path': 'sub-12345/ses-sesTEST',
                    'ignore': False
                    }
                },
            u'type': u'tabular'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_project(self):
        """ """
        # Define context
        context = {
            'container_type': 'project',
            'parent_container_type': 'group',
            'project': {'label': 'Project_Label_Test'},
            'subject': None,
            'session': None,
            'acquisition': None,
            'file': {},
            'ext': '.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Acknowledgements': '',
                    'Authors': [],
                    'BIDSVersion': '1.0.2',
                    'DatasetDOI': '',
                    'Funding': '',
                    'HowToAcknowledge': '',
                    'License': '',
                    'Name': 'Project_Label_Test',
                    'ReferencesAndLinks': [],
                    'template': 'project'
                    }
                },
                'label': 'Project_Label_Test'
            }
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_project_file(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': None,
            'subject': None,
            'session': None,
            'acquisition': None,
            'file': {u'classification': {},
                    u'type': u'archive'},
            'ext': '.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'project_file',
                    'Filename': '', 'Folder': '', 'Path': '',
                    'ignore': False
                    }
                },
            u'classification': {}, u'type': u'archive'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_project_file_multiple_measurements(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'acquisition': {u'label': u'acqTEST'},
            'file': {
                u'classification': {u'Measurement': [u'T1', u'T2'], u'Intent': u'Structural'},
                u'type': u'nifti'
            },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'template': 'anat_file',
                    'Filename': u'sub-001_ses-sesTEST_T1w.nii.gz',
                    'Path': u'sub-001/ses-sesTEST/anat', 'Folder': 'anat',
                    'Run': '', 'Acq': '', 'Ce': '', 'Rec': '',
                    'Modality': 'T1w', 'Mod': '',
                    'ignore': False
                    }
                },
            u'classification': {u'Measurement': [u'T1', u'T2'], u'Intent': u'Structural'}, u'type': u'nifti'}
        print(container)
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_BIDS_NA(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST', 'info': {'BIDS': {'Label': u'sesTEST', 'Subject': u'001'}}},
            'run_counters': utils.RunCounterMap(),
            'acquisition': {u'label': u'acq_task-TEST_run+'},
            'file': {u'classification': {u'Intent': u'Functional'},
                    u'type': u'nifti','info': {'BIDS': 'NA'}
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            u'classification': {u'Intent': u'Functional'},
            u'type': u'nifti',
            'info': {'BIDS': 'NA'}
        }

        self.assertEqual(container, container_expected)

    def assertEqual(self, a, b):
        a = utils.normalize_strings(a)
        b = utils.normalize_strings(b)

        unittest.TestCase.assertEqual(self, a, b)


if __name__ == "__main__":

    unittest.main()
    run_module_suite()
