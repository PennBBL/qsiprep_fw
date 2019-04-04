import csv
import datetime
import json
import os
import shutil
import unittest
import dateutil.parser

import flywheel

from flywheel_bids import export_bids
from flywheel_bids.supporting_files.errors import BIDSExportError

class BidsExportTestCases(unittest.TestCase):

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
        os.mkdir(self.testdir)
        # Call function
        export_bids.validate_dirname(self.testdir)

    def test_validate_dirname_doesnotexist(self):
        """ Assert function raises error when dirname does not exist"""
        # Define path that does not exist
        dirname = '/pathdoesnotexist'
        # Assert BIDSExportError raised
        with self.assertRaises(BIDSExportError) as err:
            export_bids.validate_dirname(dirname)

    def test_validate_dirname_file(self):
        """ Assert function raises error when file used as an input"""
        # Get filename of the test script
        filename = os.path.abspath(__file__)
        # Assert BIDSExportError raised
        with self.assertRaises(BIDSExportError) as err:
            export_bids.validate_dirname(filename)

    def test_define_path_valid(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {
                'info': {
                    namespace: {
                        'Path': '',
                        'Folder': '/',
                        'Filename': 'test.json'
                        }
                    }
                }
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is as expected
        self.assertEqual(path,
                '/test/test.json'
                )

    def test_define_path_empty_filename(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {
                'info': {
                    namespace: {
                        'Path': '/this/is/the/path',
                        'Folder': 'path',
                        'Filename': ''
                        }
                    }
                }
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_define_path_no_info(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {'test': {'test2': 'abcdef'}}
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_define_path_no_namespace(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {'info': {'test2': 'abcdef'}}
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_define_path_namespace_is_NA(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {'info': {namespace: 'NA'}}
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_create_json_BIDS_present(self):
        """ """
        # Define inputs
        bids_info = {
                'BIDS': {
                    'test1': 'abc',
                    'test2': 'def'
                    },
                'test1': 'abc',
                'test2': 'def'
                }
        os.mkdir(self.testdir)
        path = os.path.join(self.testdir, 'test.json')
        # Call function
        export_bids.create_json(bids_info, path, 'BIDS')
        # Ensure JSON file is created
        self.assertTrue(os.path.exists(path))

    def test_create_json_BIDS_notpresent(self):
        """ """
        # Define inputs
        bids_info = {
                'test1': 'abc',
                'test2': 'def'
                }
        os.mkdir(self.testdir)
        path = os.path.join(self.testdir, 'test.json')
        # Call function
        export_bids.create_json(bids_info, path, 'BIDS')
        # Ensure JSON file is created
        self.assertTrue(os.path.exists(path))

    def test_create_json_func_taskname(self):
        """ """
        # Define inputs
        bids_info = {
                'BIDS': {'Task': 'testtaskname'},
                'test1': 'abc',
                'test2': 'def'
                }
        os.mkdir(self.testdir)
        dirname = os.path.join(self.testdir, 'func')
        os.mkdir(dirname)
        path = os.path.join(dirname, 'test.json')
        # Call function
        export_bids.create_json(bids_info, path, 'BIDS')
        # Ensure JSON file is created
        self.assertTrue(os.path.exists(path))
        # Read in the JSON file, and assert
        with open(path, 'r') as jsonfile:
            json_contents = json.load(jsonfile)
        # Check 'TaskName' is in JSON and correct
        self.assertEqual(json_contents['TaskName'],
                'testtaskname')

    def test_exclude_containers(self):
        container = {
            'info': {
                'BIDS': {
                    'template': 'acquisition',
                    'ignore': False
                }
            },
            'label': 'Acquisition_Label_Test'
        }
        self.assertTrue(not export_bids.is_container_excluded(container, 'BIDS'))
        container = {
            'info': {
                'BIDS': {
                    'template': 'acquisition',
                    'ignore': True
                }
            },
            'label': 'Acquisition_Label_Test'
        }
        self.assertTrue(export_bids.is_container_excluded(container, 'BIDS'))

    def test_exclude_files(self):
        modifiedTimestamp = dateutil.parser.parse("2018-03-28T20:40:59.54Z")
        is_file_excluded = export_bids.is_file_excluded_options('BIDS', True, False)
        # Test ignored files
        container = {
            'info': {
                'BIDS': {
                    'template': 'func_file',
                    'ignore': False
                }
            },
            'modified': modifiedTimestamp
        }
        self.assertFalse(is_file_excluded(container, 'filePath'))
        container = {
            'info': {
                'BIDS': {
                    'template': 'func_file',
                    'ignore': True
                }
            },
            'modified': modifiedTimestamp
        }
        self.assertTrue(is_file_excluded(container, 'filePath'))

        # Test up to date files that are already downloaded
        is_file_excluded = export_bids.is_file_excluded_options('BIDS', True, True)
        modifiedSinceEpoch = (modifiedTimestamp-export_bids.EPOCH).total_seconds()
        container['info']['BIDS']['ignore'] = False
        open('filePath', 'a').close()
        os.utime('filePath', (modifiedSinceEpoch, modifiedSinceEpoch))
        print(os.path.getmtime('filePath'))

        self.assertTrue(is_file_excluded(container, 'filePath'))

        container['modified'] = dateutil.parser.parse("2718-03-28T20:40:59.54Z") # 700 years in the future
        self.assertTrue(not is_file_excluded(container, 'filePath'))

        # Test source data and derived data are excluded
        is_file_excluded = export_bids.is_file_excluded_options('BIDS', False, True)

        container['info']['BIDS']['Path'] = 'sourcedata/file'
        self.assertTrue(is_file_excluded(container, 'filePath'))

        # Test source data and derived data are not excluded
        is_file_excluded = export_bids.is_file_excluded_options('BIDS', True, True)

        container['info']['BIDS']['Path'] = 'sourcedata/file'
        self.assertTrue(not is_file_excluded(container, 'filePath'))

        os.remove('filePath')

    def test_determine_single_container(self):
        ctype = 'session'
        cid = '123456789009876543211224'
        self.assertTrue(export_bids.determine_container(None, None, ctype, cid) == (ctype, cid))


if __name__ == "__main__":

    unittest.main()
    run_module_suite()
