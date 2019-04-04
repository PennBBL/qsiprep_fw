import copy
import csv
import json
import os
import shutil
import unittest

import flywheel

from flywheel_bids import upload_bids

class BidsUploadTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def _create_json(self, filename, contents):
        with open(filename, 'w') as fp:
            fp.write(json.dumps(contents))

    def _create_tsv(self, filename, contents):
        with open(filename, 'w') as fp:
            writer = csv.writer(fp, delimiter='\t')
            for row in contents:
                writer.writerow(row)

    def test_validate_dirname_valid(self):
        """ Assert function does not raise error when valid dirname an input"""
        # Get directory the test script is in...
        dirname = os.path.dirname(os.path.abspath(__file__))
        # Call function
        upload_bids.validate_dirname(dirname)

    def test_validate_dirname_doesnotexist(self):
        """ Assert function raises error when dirname does not exist"""
        # Define path that does not exist
        dirname = '/pathdoesnotexist'
        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            upload_bids.validate_dirname(dirname)

    def test_validate_dirname_file(self):
        """ Assert function raises error when file used as an input"""
        # Get filename of the test script
        filename = os.path.abspath(__file__)

        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            upload_bids.validate_dirname(filename)

    def test_parse_bids_dir_valid(self):
        """ """
        pass

    def test_handle_project_label_group(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'group_id': {
                    'project_label': {
                        'files': ['CHANGES', 'dataset_description.json'],
                        'code1': {'files': ['debug.py']},
                        'code2': {'files': ['debug.py']},
                        'sub-01': {
                            'files': [],
                            'anat': {'files': ['test.nii.gz']},
                            'dwi': {'files': ['test.nii.gz']},
                            'func': {'files': ['test.nii.gz']}}}}}
        project_label_cli = None
        rootdir = '/root'
        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)

    def test_handle_project_label_project_nocli(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'project_label': {
                    'files': ['CHANGES', 'dataset_description.json'],
                    'code1': {'files': ['debug.py']},
                    'code2': {'files': ['debug.py']},
                    'sub-01': {
                        'files': [],
                        'anat': {'files': ['test.nii.gz']},
                        'dwi': {'files': ['test.nii.gz']},
                        'func': {'files': ['test.nii.gz']}}}}
        project_label_cli = None
        rootdir = '/root'
        # Call function
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)
        # Assert output is as expected
        self.assertEqual(bids_hierarchy_returned,
                bids_hierarchy)
        # Assert rootdir is expected
        self.assertEqual(rootdir_returned, rootdir)

    def test_handle_project_label_project_cli(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'project_label': {
                    'files': ['CHANGES', 'dataset_description.json'],
                    'code1': {'files': ['debug.py']},
                    'code2': {'files': ['debug.py']},
                    'sub-01': {
                        'files': [],
                        'anat': {'files': ['test.nii.gz']},
                        'dwi': {'files': ['test.nii.gz']},
                        'func': {'files': ['test.nii.gz']}}}}
        project_label_cli = 'new_project_label'
        rootdir = '/root'
        # Call function
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)
        # Assert output is as expected
        bids_hierarchy_expected = {
                'new_project_label': {
                    'files': ['CHANGES', 'dataset_description.json'],
                    'code1': {'files': ['debug.py']},
                    'code2': {'files': ['debug.py']},
                    'sub-01': {
                        'files': [],
                        'anat': {'files': ['test.nii.gz']},
                        'dwi': {'files': ['test.nii.gz']},
                        'func': {'files': ['test.nii.gz']}}}}
        self.assertEqual(bids_hierarchy_returned,
                bids_hierarchy_expected)
        # Assert rootdir is expected
        self.assertEqual(rootdir_returned, rootdir)

    def test_handle_project_label_sub_nocli(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'files': ['CHANGES', 'dataset_description.json'],
                'code1': {'files': ['debug.py']},
                'code2': {'files': ['debug.py']},
                'sub-01': {
                    'files': [],
                    'anat': {'files': ['test.nii.gz']},
                    'dwi': {'files': ['test.nii.gz']},
                    'func': {'files': ['test.nii.gz']}}
                }
        project_label_cli = None
        rootdir = '/root/sub-01'
        # Call function -- assert error raised because project label cannot be determined
        with self.assertRaises(SystemExit) as err:
            bids_hierarchy_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)
    def test_handle_project_label_sub_cli(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'files': ['CHANGES', 'dataset_description.json'],
                'code1': {'files': ['debug.py']},
                'code2': {'files': ['debug.py']},
                'sub-01': {
                    'files': [],
                    'anat': {'files': ['test.nii.gz']},
                    'dwi': {'files': ['test.nii.gz']},
                    'func': {'files': ['test.nii.gz']}}
                }
        project_label_cli = 'new_project_label'
        rootdir = '/root/sub-01'
        # Call function
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)
        # Assert output is as expected
        bids_hierarchy_expected = {project_label_cli: bids_hierarchy}
        bids_hierarchy_expected[project_label_cli]['files'] = []
        self.assertEqual(bids_hierarchy_returned,
                bids_hierarchy_expected)
        # Assert rootdir is expected
        self.assertEqual(rootdir_returned, '/root')

    def test_handle_project_label_files(self):
        """ """
        # Define inputs
        bids_hierarchy = {'files': ['debug.py']}
        project_label_cli = None
        rootdir = '/root'
        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            bids_hierarchy_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)

    def test_handle_project_label_sourcedata(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'project_label': {
                    'files': ['CHANGES', 'dataset_description.json'],
                    'code1': {'files': ['debug.py']},
                    'code2': {'files': ['debug.py']},
                    'sub-01': {
                        'files': [],
                        'anat': {'files': ['test.nii.gz']},
                        'dwi': {'files': ['test.nii.gz']},
                        'func': {'files': ['test.nii.gz']}},
                    'sourcedata': {
                        'sub-01': {
                            'files': [],
                            'anat': {'files': ['test.dcm.gz']},
                            'dwi': {'files': ['test.dcm.gz']},
                            'func': {'files': ['test.dcm.gz']}
                        }
                    }
                }
            }
        project_label_cli = None
        rootdir = '/root'
        # Call function
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                True, None, None)
        # Assert output is as expected
        self.assertEqual(bids_hierarchy_returned,
                bids_hierarchy)
        # Assert rootdir is expected
        self.assertEqual(rootdir_returned, rootdir)
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)
        # Assert output is as expected
        bids_hierarchy['project_label'].pop('sourcedata')
        self.assertEqual(bids_hierarchy_returned,
                bids_hierarchy)
        # Assert rootdir is expected
        self.assertEqual(rootdir_returned, rootdir)

    def test_handle_project_label_subject_not_found(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'files': ['CHANGES', 'dataset_description.json'],
                'code1': {'files': ['debug.py']},
                'code2': {'files': ['debug.py']},
                'sub-01': {
                        'ses-01': {
                            'files': [],
                            'anat': {'files': ['test.nii.gz']},
                            'dwi': {'files': ['test.nii.gz']},
                            'func': {'files': ['test.nii.gz']}
                        },
                        'ses-02': {
                            'files': [],
                            'anat': {'files': ['test.nii.gz']},
                            'dwi': {'files': ['test.nii.gz']},
                            'func': {'files': ['test.nii.gz']}
                        }
                    }
                }
        project_label_cli = 'new_project_label'
        rootdir = '/root/sub-01'
        # Call function
        with self.assertRaises(SystemExit) as err:
            bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                    copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                    False, 'sub-03', None)

    def test_handle_project_label_single_subject(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'files': ['CHANGES', 'dataset_description.json'],
                'code1': {'files': ['debug.py']},
                'code2': {'files': ['debug.py']},
                'sub-02': {
                    'files': [],
                    'anat': {'files': ['test.nii.gz']},
                    'dwi': {'files': ['test.nii.gz']},
                    'func': {'files': ['test.nii.gz']}},
                'sub-01': {
                    'files': [],
                    'anat': {'files': ['test.nii.gz']},
                    'dwi': {'files': ['test.nii.gz']},
                    'func': {'files': ['test.nii.gz']}}
                }
        project_label_cli = 'new_project_label'
        rootdir = '/root/sub-01'
        # Call function
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, 'sub-02', None)
        # Assert output is as expected
        bids_hierarchy_expected = {project_label_cli: {'sub-02': bids_hierarchy['sub-02']}}
        bids_hierarchy_expected[project_label_cli]['files'] = []
        self.assertEqual(bids_hierarchy_returned,
                bids_hierarchy_expected)
        # Assert rootdir is expected
        self.assertEqual(rootdir_returned, '/root')

    def test_handle_project_label_session_not_found(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'files': ['CHANGES', 'dataset_description.json'],
                'code1': {'files': ['debug.py']},
                'code2': {'files': ['debug.py']},
                'sub-01': {
                        'ses-01': {
                            'files': [],
                            'anat': {'files': ['test.nii.gz']},
                            'dwi': {'files': ['test.nii.gz']},
                            'func': {'files': ['test.nii.gz']}
                        },
                        'ses-02': {
                            'files': [],
                            'anat': {'files': ['test.nii.gz']},
                            'dwi': {'files': ['test.nii.gz']},
                            'func': {'files': ['test.nii.gz']}
                        }
                    }
                }
        project_label_cli = 'new_project_label'
        rootdir = '/root/sub-01'
        # Call function
        with self.assertRaises(SystemExit) as err:
            bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                    copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                    False, 'sub-01', 'ses-03')

    def test_handle_project_label_single_session(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                'files': ['CHANGES', 'dataset_description.json'],
                'code1': {'files': ['debug.py']},
                'code2': {'files': ['debug.py']},
                'sub-01': {
                        'ses-01': {
                            'files': [],
                            'anat': {'files': ['test.nii.gz']},
                            'dwi': {'files': ['test.nii.gz']},
                            'func': {'files': ['test.nii.gz']}
                        },
                        'ses-02': {
                            'files': [],
                            'anat': {'files': ['test.nii.gz']},
                            'dwi': {'files': ['test.nii.gz']},
                            'func': {'files': ['test.nii.gz']}
                        }
                    }
                }
        project_label_cli = 'new_project_label'
        rootdir = '/root/sub-01'
        # Call function
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, 'sub-01', 'ses-02')
        # Assert output is as expected
        bids_hierarchy_expected = {project_label_cli: {'sub-01': {'ses-02': bids_hierarchy['sub-01']['ses-02']}}}
        bids_hierarchy_expected[project_label_cli]['files'] = []
        bids_hierarchy_expected[project_label_cli]['sub-01']['files'] = []
        self.assertEqual(bids_hierarchy_returned,
                bids_hierarchy_expected)
        # Assert rootdir is expected
        self.assertEqual(rootdir_returned, '/root')


    def test_handle_project_label_failure(self):
        """ """
        # Define inputs
        bids_hierarchy = {
                '7t_trt_reduced': {
                    'files': ['dataset_description.json'],
                    'sub-01': {
                        'files': ['sub-01_sessions.tsv'],
                        'ses-1': {
                            'files': ['sub-01_ses-1_scans.tsv'],
                            'fmap': {'files': ['sub-01_ses-1_run-1_magnitude1.nii.gz']},
                            'anat': {'files': ['sub-01_ses-1_T1map.nii.gz']},
                            'func': {'files': ['sub-01_ses-1_task-rest_acq-fullbrain_run-1_bold.nii.gz']}},
                        'ses-2': {
                            'files': ['sub-01_ses-2_scans.tsv'],
                            'fmap': {'files': ['sub-01_ses-2_run-1_magnitude1.nii.gz']},
                            'func': {'files': ['sub-01_ses-2_task-rest_acq-fullbrain_run-1_bold.nii.gz']}}},
                    'sub-02': {
                        'files': ['sub-02_sessions.tsv'],
                        'ses-1': {
                            'files': ['sub-02_ses-1_scans.tsv'],
                            'fmap': {'files': ['sub-02_ses-1_run-1_magnitude1.nii.gz']},
                            'anat': {'files': ['sub-02_ses-1_T1map.nii.gz']},
                            'func': {'files': ['sub-02_ses-1_task-rest_acq-fullbrain_run-1_bold.nii.gz']}},
                        'ses-2': {
                            'files': ['sub-02_ses-2_scans.tsv'],
                            'fmap': {'files': ['sub-02_ses-2_run-1_magnitude1.nii.gz']},
                            'func': {'files': ['sub-02_ses-2_task-rest_acq-fullbrain_run-1_bold.nii.gz']}}}}}
        project_label_cli = 'new_project_label'
        rootdir = '/root'
        # Call function
        bids_hierarchy_returned, rootdir_returned = upload_bids.handle_project_label(
                copy.deepcopy(bids_hierarchy), project_label_cli, rootdir,
                False, None, None)

    def test_determine_acquisition_label_bids(self):
        """ """
        foldername = 'anat'
        fname = 'sub-01_ses-01_T1w.nii.gz'
        hierarchy_type = 'BIDS'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert the foldername is used as the acquisition label
        self.assertEqual(foldername, acq_label)

    def test_determine_acquisition_label_flywheel_T1w(self):
        """ """
        foldername = 'anat'
        fname = 'sub-control01_ses-01_T1w.nii.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('T1w', acq_label)

    def test_determine_acquisition_label_flywheel_dwi(self):
        """ """
        foldername = 'dwi'
        fname = 'sub-control01_ses-01_task-nback_dwi.nii.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback_dwi', acq_label)

    def test_determine_acquisition_label_flywheel_niigz(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_bold.nii.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_json(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_bold.json'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_eventstsv(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_events.tsv'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_physio(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_physio.tsv.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_physiojson(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_physio.json'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_stim(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_stim.tsv.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_stimjson(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_stim.json'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_classify_acquisition_T1w(self):
        """ Assert T1w image classified as anatomy_t1w """
        full_fname = '/sub-01/ses-123/anat/sub-01_ses-123_T1w.nii.gz'
        classification = upload_bids.classify_acquisition(full_fname)
        self.assertEqual({'Intent': ['Structural'], 'Measurement': ['T1']}, classification)

    def test_classify_acquisition_T2w(self):
        """ Assert T2w image classified as anatomy_t2w """
        full_fname = '/sub-01/anat/sub-01_T2w.nii.gz'
        classification = upload_bids.classify_acquisition(full_fname)
        self.assertEqual({'Intent': ['Structural'], 'Measurement': ['T2']}, classification)


    def test_fill_in_properties_anat(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_ce-label1_rec-label2_run-01_mod-label3_T1w.nii.gz',
                    'info': {
                        'BIDS': {
                            'Ce': '',
                            'Rec': '',
                            'Run': '',
                            'Mod': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'anat'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Ce': 'label1',
                    'Rec': 'label2',
                    'Run': '01',
                    'Mod': 'label3',
                    'Modality': 'T1w',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name, True)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_func(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii',
                'file': {
                    'name': 'sub-01_ses-01_task-label1_acq-01_rec-label2_run-01_echo-2_bold.nii',
                    'info': {
                        'BIDS': {
                            'Task': '',
                            'Rec': '',
                            'Run': '',
                            'Echo': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'func'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Task': 'label1',
                    'Rec': 'label2',
                    'Run': '01',
                    'Echo': '2',
                    'Modality': 'bold',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name, True)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_dicoms_without_local_values(self):
        """ """
        # Define inputs
        context = {
                'ext': '.dcm.zip',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_ce-label1_rec-label2_run-01_mod-label3_T1w.dcm.zip',
                    'info': {
                        'BIDS': {
                            'Ce': '',
                            'Rec': '',
                            'Run': '03',
                            'Mod': '',
                            'Modality': '',
                            'Folder': 'sourcedata',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'anat'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Ce': 'label1',
                    'Rec': 'label2',
                    'Run': '03',
                    'Mod': 'label3',
                    'Modality': 'T1w',
                    'Folder': 'sourcedata',
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name, False)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_dwi(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_run-01_dwi.nii.gz',
                    'info': {
                        'BIDS': {
                            'Run': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'dwi'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Run': '01',
                    'Modality': 'dwi',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name, True)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_fmap1(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_run-03_phasediff.nii.gz',
                    'info': {
                        'BIDS': {
                            'Run': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'fmap'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Run': '03',
                    'Modality': 'phasediff',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name, True)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_fmap2(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_dir-label1_run-03_epi.nii.gz',
                    'info': {
                        'BIDS': {
                            'Dir': '',
                            'Run': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'fmap'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Dir': 'label1',
                    'Run': '03',
                    'Modality': 'epi',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name, True)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_parse_json_valid(self):
        """ """
        # Create json file
        os.mkdir(self.testdir)
        filename = os.path.join(self.testdir, 'test.json')
        contents = {
                'test1': {'_id': '123', 'id_type': 'test'},
                }
        self._create_json(filename, contents)
        # Call function
        parsed_contents = upload_bids.parse_json(filename)
        # Assert parsed is the same as original contents
        self.assertEqual(parsed_contents, contents)

    def test_compare_json_to_file_match1(self):
        """ """
        json_filename = 'task-rest_acq-fullbrain_bold.json'
        filename = 'sub-01_ses-1_task-rest_acq-fullbrain_run-1_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertTrue(match)

    def test_compare_json_to_file_match2(self):
        """ """
        json_filename = 'task-rest_acq-fullbrain_bold.json'
        filename = 'sub-01_ses-1_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertTrue(match)

    def test_compare_json_to_file_match3(self):
        """ """
        json_filename = 'task-rest_acq-fullbrain_bold.json'
        filename = 'sub-01_ses-2_task-rest_acq-fullbrain_run-1_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertTrue(match)

    def test_compare_json_to_file_match4(self):
        """ """
        json_filename = 'task-rest_acq-fullbrain_bold.json'
        filename = 'sub-01_ses-2_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertTrue(match)

    def test_compare_json_to_file_match5(self):
        """ """
        json_filename = 'sub-01_ses-1_run-2_phasediff.json'
        filename = 'sub-01_ses-1_run-2_phasediff.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertTrue(match)

    def test_compare_json_to_file_match6(self):
        """ """
        json_filename = 'task-rest_acq-prefrontal_physio.json'
        filename = 'sub-02_ses-2_task-rest_acq-prefrontal_physio.tsv.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertTrue(match)

    def test_compare_json_to_file_nomatch1(self):
        """ """
        json_filename = 'task-rest_acq-fullbrain_run-1_physio.json'
        filename = 'sub-01_ses-2_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertFalse(match)

    def test_compare_json_to_file_nomatch2(self):
        """ """
        json_filename = 'task-rest_acq-prefrontal_bold.json'
        filename = 'sub-01_ses-2_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertFalse(match)

    def test_compare_json_to_file_nomatch3(self):
        """ """
        json_filename = 'task-rest_acq-fullbrain_run-2_physio.json'
        filename = 'sub-01_ses-2_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertFalse(match)

    def test_compare_json_to_file_nomatch4(self):
        """ """
        json_filename = 'task-rest_acq-prefrontal_physio.json'
        filename = 'sub-01_ses-2_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertFalse(match)

    def test_compare_json_to_file_nomatch5(self):
        """ """
        json_filename = 'sub-01_ses-1_run-1_phasediff.json'
        filename = 'sub-01_ses-1_run-2_phasediff.nii.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertFalse(match)

    def test_compare_json_to_file_nomatch6(self):
        """ """
        json_filename = 'task-rest_acq-prefrontal_physio.json'
        filename = 'sub-02_ses-2_task-rest_acq-fullbrain_run-2_physio.tsv.gz'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertFalse(match)

    def test_compare_json_to_file_nomatch_notnifti(self):
        """ """
        json_filename = 'sub-01_ses-1_run-1_phasediff.json'
        filename = 'sub-01_ses-1_run-1_phasediff.tsv'
        match = upload_bids.compare_json_to_file(json_filename, filename)
        self.assertFalse(match)

    def test_parse_tsv_valid(self):
        """ """
        # Create tsv file
        os.mkdir(self.testdir)
        filename = os.path.join(self.testdir, 'test.tsv')
        contents = [
                ['title', 'id', 'id_type'],
                ['test1', '123', 'test2']
                ]
        self._create_tsv(filename, contents)
        # Call function
        contents_parsed = upload_bids.parse_tsv(filename)
        # Expected contents
        contents_expected = [
                ['title', 'id', 'id_type'],
                ['test1', 123, 'test2']
                ]
        # Assert parsed is the same as original contents
        self.assertEqual(contents_parsed,
                contents_expected)

    def test_convert_dtype_valid(self):
        """ """
        # Define contents
        contents = [
                ['participant_id', 'sex', 'age_at_first_scan_years', 'number_of_scans_before', 'handedness'],
                ['sub-01', 'F', '29', '17', '100'],
                ['sub-02', 'F', '23', '6', '100'],
                ['sub-03', 'M', '25', '18', '86'],
                ]
        # Call function
        contents_converted = upload_bids.convert_dtype(contents)
        # Define expected contents
        contents_expected = [
                ['participant_id', 'sex', 'age_at_first_scan_years', 'number_of_scans_before', 'handedness'],
                ['sub-01', 'female', 29, 17, 100],
                ['sub-02', 'female', 23, 6, 100],
                ['sub-03', 'male', 25, 18, 86],
                ]
        # Assert equal
        self.assertEqual(contents_converted,
                contents_expected)

    def test_convert_dtype_2rows(self):
        # Define contents
        contents = [
                ['session', 'sex', 'test1', 'test2'],
                ['ses-1', 'F', '1', '1.2']
                ]
        # Call function
        contents_converted = upload_bids.convert_dtype(contents)
        # Define expected contents
        contents_expected = [
                ['session', 'sex', 'test1', 'test2'],
                ['ses-1', 'female', 1, 1.2]
                ]
        # Assert equal
        self.assertEqual(contents_converted,
                contents_expected)

    def test_convert_dtype_filename(self):
        # Define contents
        contents = [
                ['filename', 'positive'],
                ['bold1.nii.gz', '1'],
                ['bold2.nii.gz', '9'],
                ['bold3.nii.gz', '7']
                ]
        # Call function
        contents_converted = upload_bids.convert_dtype(contents)
        # Define expected contents
        contents_expected = [
                ['filename', 'positive'],
                ['bold1.nii.gz', 1],
                ['bold2.nii.gz', 9],
                ['bold3.nii.gz', 7]
                ]
        # Assert equal
        self.assertEqual(contents_converted,
                contents_expected)

    def test_convert_dtype_male_female(self):
        # Define contents
        contents = [
                ['session', 'sex'],
                ['ses-1', 'F'],
                ['ses-2', 'M'],
                ['ses-3', 'F'],
                ['ses-4', 'F'],
                ['ses-5', 'M'],
                ]
        # Call function
        contents_converted = upload_bids.convert_dtype(contents)
        # Define expected contents
        contents_expected = [
                ['session', 'sex'],
                ['ses-1', 'female'],
                ['ses-2', 'male'],
                ['ses-3', 'female'],
                ['ses-4', 'female'],
                ['ses-5', 'male'],
                ]

        # Assert equal
        self.assertEqual(contents_converted,
                contents_expected)



if __name__ == "__main__":

    unittest.main()
    run_module_suite()
