import jsonschema
import os
import shutil
import unittest

import flywheel
from flywheel_bids.supporting_files import utils

class UtilsTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def test_get_extension_nii(self):
        """ Get extension if .nii """
        fname = 'T1w.nii'
        ext = utils.get_extension(fname)
        self.assertEqual('.nii', ext)

    def test_get_extension_niigz(self):
        """ Get extension if .nii.gz """
        fname = 'T1w.nii.gz'
        ext = utils.get_extension(fname)
        self.assertEqual('.nii.gz', ext)

    def test_get_extension_tsv(self):
        """ Get extension if .tsv """
        fname = 'T1w.tsv'
        ext = utils.get_extension(fname)
        self.assertEqual('.tsv', ext)

    def test_get_extension_none(self):
        """ Assert function returns None if no extension present """
        fname = 'sub-01_T1w'
        ext = utils.get_extension(fname)
        self.assertIsNone(ext)

    def test_get_extension_fix1(self):
        """ """
        fname = '1.2.3.4.5.6.nii.gz'
        ext = utils.get_extension(fname)
        self.assertEqual('.nii.gz', ext)

    def test_get_extension_fix2(self):
        """ """
        fname = '1.2.3.4.5.json'
        ext = utils.get_extension(fname)
        self.assertEqual('.json', ext)

    def test_get_extension_fix3(self):
        """ """
        fname = 'test.tar.gz'
        ext = utils.get_extension(fname)
        self.assertEqual('.tar.gz', ext)

    def test_get_extension_fix4(self):
        """ """
        fname = 'test.tsv'
        ext = utils.get_extension(fname)
        self.assertEqual('.tsv', ext)

    def test_get_extension_fix5(self):
        """ """
        fname = 'T1w.nii'
        ext = utils.get_extension(fname)
        self.assertEqual('.nii', ext)

    def test_get_extension_fix6(self):
        """ """
        fname = '{T1w.info}kajsdfk.nii.gz'
        ext = utils.get_extension(fname)
        self.assertEqual('.nii.gz', ext)

    @unittest.skip("Integration test")
    def test_validate_project_label_invalidproject(self):
        """ Get project that does not exist. Assert function returns None.

        NOTE: the environment variable $APIKEY needs to be defined with users API key
        """
        client = flywheel.Flywheel(os.environ['APIKEY'])
        label = 'doesnotexistdoesnotexistdoesnotexist89479587349'
        with self.assertRaises(SystemExit):
            utils.validate_project_label(client, label)

    @unittest.skip("Integration test")
    def test_validate_project_label_validproject(self):
        """ Get project that DOES exist. Assert function returns the project.

        NOTE: the environment variable $APIKEY needs to be defined with users API key

        """
        client = flywheel.Flywheel(os.environ['APIKEY'])
        label = 'Project Name'
        project_id = utils.validate_project_label(client, label)
        project_id_expected = u'58175ad3de26e00012c69306'
        self.assertEqual(project_id, project_id_expected)


if __name__ == "__main__":

    unittest.main()
    run_module_suite()
