import os
import shutil
import unittest

import flywheel

from flywheel_bids import curate_bids
from flywheel_bids.supporting_files import project_tree
from flywheel_bids.supporting_files.templates import BIDS_TEMPLATE

class BidsCurateTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def test_validate_meta_info_valid1(self):
        """ """
        # Define meta information
        meta_info = {'info': {'BIDS': {}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid2(self):
        """ """
        # Define meta information - Path is empty string - this is ok!!
        meta_info = {'info': {'BIDS': {'Path': '', 'extra': 'test'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid3(self):
        """ """
        # Define meta information - Folder is empty string - this is ok!!
        meta_info = {'info': {'BIDS': {'Folder': '', 'extra': 'test'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid4(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {
            'Run': '', 'Ce': '',
            'Mod': '', 'Acq': '', 'Rec': ''}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid5(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {'Run': 1}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')
        # Assert run numebr is still an integer
        self.assertEqual(meta_info['info']['BIDS']['Run'], 1)

    def test_validate_meta_info_invalid1(self):
        """ """
        # Define meta information - Task value is missing
        meta_info = {'info': {'BIDS': {'template': 'task_events_file', 'Filename': 'example.tsv', 'Task': '', 'Modality': 'bold'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                u"Task '' does not match '^[a-zA-Z0-9]+$'")

    def test_validate_meta_info_invalid2(self):
        """ """
        # Define meta information - Filename is missing
        meta_info = {'info': {'BIDS': {'template': 'anat_file', 'Filename': '', 'extra': 'test'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
               u"Filename '' is too short\n'Modality' is a required property") 

    def test_validate_meta_info_invalid3(self):
        """ """
        # Define meta information - Modality value is missing
        meta_info = {'info': {'BIDS': {'template': 'anat_file', 'Filename': 'example.nii.gz', 'Modality': ''}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                "Modality '' is not one of ['T1w', 'T2w', 'T1rho', 'T1map', 'T2map', 'FLAIR', 'FLASH', 'PD',"+\
                " 'PDmap', 'PDT2', 'inplaneT1', 'inplaneT2', 'angio', 'defacemask', 'SWImagandphase']")

    def test_validate_meta_info_invalid4(self):
        """ """
        # Define meta information - invalid/unknown/NO_MATCH template
        meta_info = {'info': {'BIDS': {'template': 'NO_MATCH', 'Modality': 'bold'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                'Unknown template: NO_MATCH. ')

    def test_validate_meta_info_invalid5(self):
        """ """
        # Define meta information - Task is empty,
        meta_info = {'info': {'BIDS': {'template': 'func_file', 'Filename': 'example.nii.gz',
            'Modality': 'sbref', 'Task': '', 'Rec': '', 'Run': '01', 'Echo': 'AA'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                "Task '' does not match '^[a-zA-Z0-9]+$'\nEcho 'AA' does not match '^[0-9]*$'")

    def test_validate_meta_info_invalid_characters1(self):
        """ """
        # Define meta information - invalid characters in multiple keys
        meta_info = {'info': {'BIDS': {
            'template': 'anat_file',
            'Modality': 'invalid._#$*%',
            'Ce': 'invalid2.',
            'Mod': '_invalid2',
            'Filename': ''
            }}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                "Filename '' is too short\n"+\
                "Mod '_invalid2' does not match '^[a-zA-Z0-9]*$'\n"+\
                "Modality 'invalid._#$*%' is not one of ['T1w', 'T2w', 'T1rho', 'T1map', 'T2map', 'FLAIR', 'FLASH', 'PD'"+\
                ", 'PDmap', 'PDT2', 'inplaneT1', 'inplaneT2', 'angio', 'defacemask', 'SWImagandphase']\n"+\
                "Ce 'invalid2.' does not match '^[a-zA-Z0-9]*$'")

    def test_validate_meta_info_no_BIDS(self):
        """ """
        # Define meta information w/o BIDS info
        meta_info = {'info': {'test1' : 'abc', 'test2': 'def'}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS': 'NA' is in meta_info
        self.assertEqual(meta_info['info']['BIDS'], 'NA')

    def test_validate_meta_info_no_info(self):
        """ """
        # Define meta information w/o BIDS info
        meta_info = {'other_info': 'test'}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS': 'NA' is in meta_info
        self.assertEqual(meta_info['info']['BIDS'], 'NA')

    def test_validate_meta_info_BIDS_NA(self):
        """ """
        # Define meta information w/ BIDS NA
        meta_info = {'info': {'BIDS': 'NA'}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS': 'NA' is in meta_info
        self.assertEqual(meta_info['info']['BIDS'], 'NA')

    def test_validate_meta_info_already_valid(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {
            'Filename': 'sub-01_ses-02_T1w.nii.gz',
            'Modality': 'T1w',
            'valid': True,
            'error_message': ''}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_was_invalid(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {
            'Task': 'testtask', 'Modality': 'bold',
            'Filename': 'sub-01_ses-02_task-testtask_bold.nii.gz',
            'valid': False,
            'error_message': 'Missing required property: Task. ',
            }}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_intended_for(self):
        project = project_tree.TreeNode('project', { 'label': 'testProj' })

        session = project_tree.TreeNode('session', { 'label': 'session1', 'subject': { 'code': 'subj1' } })
        project.children.append(session)

        acq1 = project_tree.TreeNode('acquisition', { 'label': 'acq1_LR', 'created': '2018-01-17T07:58:09.799Z' })
        session.children.append(acq1)
        file1 = project_tree.TreeNode('file', {
            'name': 'fieldmap.nii.gz',
            'type': 'nifti',
            'classification': {'Intent': 'Fieldmap'}
        })
        acq1.children.append(file1)

        acq2 = project_tree.TreeNode('acquisition', { 'label': 'acq2_task-rest_run-1' })
        session.children.append(acq2)
        file2 = project_tree.TreeNode('file', {
            'name': 'task1.nii.gz',
            'type': 'nifti',
            'classification': {'Intent': 'Functional'}
        })
        acq2.children.append(file2)

        curate_bids.curate_bids_tree(None, project, False, None, False)
        self.assertIn('IntendedFor', file1['info'])
        self.assertEqual(len(file1['info']['IntendedFor']), 1)
        self.assertEqual(file1['info']['IntendedFor'][0], 'ses-session1/func/sub-subj1_ses-session1_task-rest_run-1_bold.nii.gz')


if __name__ == "__main__":

    unittest.main()
    run_module_suite()
