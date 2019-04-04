import argparse
import dateutil.parser
import logging
import json
import os
import re
import sys
import zipfile

import flywheel

from .supporting_files import utils
from .supporting_files.errors import BIDSExportError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bids-exporter')

EPOCH = dateutil.parser.parse('1970-01-01 00:00:0Z')

def validate_dirname(dirname):
    """
    Check the following criteria to ensure 'dirname' is valid
        - dirname exists
        - dirname is a directory
    If criteria not met, raise an error
    """
    logger.info('Verify download directory exists')

    # Check dirname is a directory
    if not os.path.isdir(dirname):
        logger.error('Path (%s) is not a directory' % dirname)
        raise BIDSExportError('Path (%s) is not a directory' % dirname)

    # Check dirname exists
    if not os.path.exists(dirname):
        logger.info('Path (%s) does not exist. Making directory...' % dirname)
        os.mkdir(dirname)

def parse_bool(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v != 0

    return str(v).lower() == 'true'

def get_metadata(ctx, namespace):
    # Check if 'info' in f object
    if 'info' not in ctx:
        return None
    # Check if namespace ('BIDS') in f object
    if namespace not in ctx['info']:
        return None
    # Check if 'info.BIDS' == 'NA'
    if ctx['info'][namespace] == 'NA':
        return None

    return ctx['info'][namespace]

def is_file_excluded_options(namespace, src_data, replace):
    def is_file_excluded(f, fpath):
        metadata = get_metadata(f, namespace)
        if not metadata:
            return True

        if parse_bool(metadata.get('ignore', False)):
            return True

        if not src_data:
            path = metadata.get('Path')
            if path and path.startswith('sourcedata'):
                return True

        # Check if file already exists
        if os.path.isfile(fpath):
            if not replace:
                return True
            # Check if the file already exists and whether it is up to date
            time_since_epoch = timestamp_to_int(f.get('modified'))
            if time_since_epoch == int(os.path.getmtime(fpath)):
                return True

        return False
    return is_file_excluded

def timestamp_to_int(timestamp):
    return int((timestamp-EPOCH).total_seconds())

def is_container_excluded(container, namespace):
    meta_info = container.get('info', {}).get(namespace, {})
    if isinstance(meta_info, dict):
        return meta_info.get('ignore', False)

def warn_if_bids_invalid(f, namespace):
    """
    Logs a warning iff info.BIDS.valid = false
    """
    metadata = get_metadata(f, namespace)
    if not metadata or metadata.get('valid') == None:
        return
    elif not parse_bool(metadata.get('valid')):
        logger.warn('File {} is not valid: {}'.format(metadata.get('Filename'), metadata.get('error_message')))

def define_path(outdir, f, namespace):
    """"""
    metadata = get_metadata(f, namespace)
    if not metadata:
        full_filename = ''
    elif metadata.get('Filename'):
        # Ensure that the folder exists...
        full_path = os.path.join(outdir,
                                 metadata['Path'])
        # Define path to download file to...
        full_filename = os.path.join(full_path, metadata['Filename'])
    else:
        full_filename = ''

    return full_filename

def get_folder(f, namespace):
    metadata = get_metadata(f, namespace)
    if not metadata:
        return ''

    return metadata.get('Folder')

def create_json(meta_info, path, namespace):
    """
    Given a dictionary of the meta info
        and the path, creates a JSON file
        with the bids info

    namespace in the template namespace,
        in this case it is 'BIDS'

    """
    # Remove the 'BIDS' value from info
    try:
        ns_data = meta_info.pop(namespace)
    except:
        ns_data = {}

    # If meta info is empty, simply return
    if not meta_info:
        return

    # If the file is functional,
    #   move the 'TaskName' from 'BIDS'
    #   to the top level
    if '/func/' in path and 'Task' in ns_data:
         meta_info['TaskName'] = ns_data['Task']

    # Perform delete and updates
    for key in ns_data.get('delete_info', []):
        meta_info.pop(key, None)

    for key, value in ns_data.get('set_info', {}).items():
        meta_info[key] = value

    # Remove extension of path and replace with .json
    ext = utils.get_extension(path)
    new_path = re.sub(ext, '.json', path)

    # Write out contents to JSON file
    with open(new_path, 'w') as outfile:
        json.dump(meta_info, outfile,
                sort_keys=True, indent=4)

def download_bids_files(fw, filepath_downloads, dry_run):
    """
    filepath_downloads: {container_type: {filepath: {'args': (tuple of args for sdk download function), 'modified': file modified attr}}}
    """
    # Download all project files
    logger.info('Downloading project files')
    for f in filepath_downloads['project']:
        args = filepath_downloads['project'][f]['args']
        modified = filepath_downloads['project'][f]['modified']
        logger.info('Downloading project file: {0}'.format(args[1]))
        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[2]))
            continue
        fw.download_file_from_project(*args)
        # Set the mtime of the downloaded file to the 'modified' timestamp in seconds
        modified_time = float(timestamp_to_int(modified))
        os.utime(f,(modified_time, modified_time))

        # If zipfile is attached to project, unzip...
        path = args[2]
        zip_pattern = re.compile('[a-zA-Z0-9]+(.zip)')
        zip_dirname = path[:-4]
        if zip_pattern.search(path):
            zip_ref = zipfile.ZipFile(path, 'r')
            zip_ref.extractall(zip_dirname)
            zip_ref.close()
            # Remove the zipfile
            os.remove(path)

    # Download all session files
    logger.info('Downloading session files')
    for f in filepath_downloads['session']:
        args = filepath_downloads['session'][f]['args']
        modified = filepath_downloads['session'][f]['modified']
        logger.info('Downloading session file: {0}'.format(args[1]))
        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[2]))
            continue
        fw.download_file_from_session(*args)
        # Set the mtime of the downloaded file to the 'modified' timestamp in seconds
        modified_time = float(timestamp_to_int(modified))
        os.utime(f,(modified_time, modified_time))


    # Download all acquisition files
    logger.info('Downloading acquisition files')
    for f in filepath_downloads['acquisition']:
        args = filepath_downloads['acquisition'][f]['args']
        modified = filepath_downloads['acquisition'][f]['modified']
        # Download the file
        logger.info('Downloading acquisition file: {0}'.format(args[1]))

        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[2]))
            continue

        fw.download_file_from_acquisition(*args)
        # Set the mtime of the downloaded file to the 'modified' timestamp in seconds
        modified_time = float(timestamp_to_int(modified))
        os.utime(f,(modified_time, modified_time))

    # Creating all JSON sidecar files
    logger.info('Creating sidecar files')
    for f in filepath_downloads['sidecars']:
        args = filepath_downloads['sidecars'][f]['args']
        # Download the file
        logger.info('Creating sidecar file: {0}'.format(args[1]))

        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[1]))
            continue

        create_json(*args)

def download_bids_dir(fw, container_id, container_type, outdir, src_data=False,
        dry_run=False, replace=False, subjects=[], sessions=[], folders=[]):
    """

    fw: Flywheel client
    project_id: Label of the project to download
    outdir: path to directory to download files to, string
    src_data: Option to include sourcedata when downloading

    """

    # Define namespace
    namespace = 'BIDS'
    is_file_excluded = is_file_excluded_options(namespace, src_data, replace)

    # Files and the corresponding download arguments separated by parent container
    filepath_downloads = {
        'project':{},
        'session':{},
        'acquisition':{},
        'sidecars':{}
    }
    valid = True

    if container_type == 'project':
        # Get project
        project = fw.get_project(container_id)

        # Check that project is curated
        if not project['info'].get(namespace):
            raise BIDSExportError('Project {} has not been curated for {}'.format(project.label, namespace))

        logger.info('Processing project files')
        # Iterate over any project files
        for f in project.get('files', []):

            # Define path - ensure that the folder exists...
            path = define_path(outdir, f, namespace)
            # If path is not defined (an empty string) move onto next file
            if not path:
                continue

            # Don't exclude any files that specify exclusion
            if is_file_excluded(f, path):
                continue

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            warn_if_bids_invalid(f, namespace)


            # For dry run, don't actually download
            if path in filepath_downloads['project']:
                logger.error('Multiple files with path {0}:\n\t{1} and\n\t{2}'.format(path, f['name'], filepath_downloads['project'][path]['args'][1]))
                valid = False

            filepath_downloads['project'][path] = {'args': (project['_id'], f['name'], path), 'modified': f.get('modified')}

        ## Create dataset_description.json filepath_download
        path = os.path.join(outdir, 'dataset_description.json')
        filepath_downloads['sidecars'][path] = {'args': (project['info'][namespace], path, namespace)}
        # Get project sessions
        project_sessions = fw.get_project_sessions(container_id)
    elif container_type == 'session':
        project_sessions = [fw.get_session(container_id)]
    else:
        project_sessions = []

    if project_sessions:
        logger.info('Processing session files')
        all_acqs = []
        for proj_ses in project_sessions:
            # Skip session if we're filtering to the list of sessions
            if sessions and proj_ses.get('label') not in sessions:
                continue

            # Skip session if BIDS.Ignore is True
            if is_container_excluded(proj_ses, namespace):
                continue

            # Skip subject if we're filtering subjects
            if subjects:
                subj_code = proj_ses.get('subject', {}).get('code')
                if subj_code not in subjects:
                    continue

            # Get true session if files aren't already retrieved, in order to access file info
            if proj_ses.get('files'):
                session = proj_ses
            else:
                session = fw.get_session(proj_ses['_id'])
            # Check if session contains files
            # Iterate over any session files
            for f in session.get('files', []):

                # Define path - ensure that the folder exists...
                path = define_path(outdir, f, namespace)
                # If path is not defined (an empty string) move onto next file
                if not path:
                    continue

                # Don't exclude any files that specify exclusion
                if is_file_excluded(f, path):
                    continue

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                warn_if_bids_invalid(f, namespace)


                if path in filepath_downloads['session']:
                    logger.error('Multiple files with path {0}:\n\t{1} and\n\t{2}'.format(path, f['name'], filepath_downloads['session'][path]['args'][1]))
                    valid = False

                filepath_downloads['session'][path] = {'args': (session['_id'], f['name'], path), 'modified': f.get('modified')}

            logger.info('Processing acquisition files')
            # Get acquisitions
            session_acqs = fw.get_session_acquisitions(proj_ses['_id'])
            all_acqs += session_acqs
    elif container_type == 'acquisition':
        all_acqs = [fw.get_acquisition(container_id)]
    else:
        all_acqs = []

    if all_acqs:
        for ses_acq in all_acqs:
            # Skip if BIDS.Ignore is True
            if is_container_excluded(ses_acq, namespace):
                continue
            # Get true acquisition if files aren't already retrieved, in order to access file info

            acq = fw.get_acquisition(ses_acq['_id'])
            # Iterate over acquistion files
            for f in acq.get('files', []):

                # Skip any folders not in the skip-list (if there is a skip list)
                if folders:
                    folder = get_folder(f, namespace)
                    if folder not in folders:
                        continue

                # Define path - ensure that the folder exists...
                path = define_path(outdir, f, namespace)
                # If path is not defined (an empty string) move onto next file
                if not path:
                    continue

                # Don't exclude any files that specify exclusion
                if is_file_excluded(f, path):
                    continue

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                warn_if_bids_invalid(f, namespace)

                if path in filepath_downloads['acquisition']:
                    logger.error('Multiple files with path {0}:\n\t{1} and\n\t{2}'.format(path, f['name'], filepath_downloads['acquisition'][path]['args'][1]))
                    valid = False

                filepath_downloads['acquisition'][path] = {'args': (acq['_id'], f['name'], path), 'modified': f.get('modified')}

                # Create the sidecar JSON filepath_download
                filepath_downloads['sidecars'][path] = {'args': (f['info'], path, namespace)}
    else:
        logger.error('{} is not a valid containertype'.format(container_type))
        valid = False

    if not valid:
        raise BIDSExportError('Error mapping files from Flywheel to BIDS')

    download_bids_files(fw, filepath_downloads, dry_run)

def determine_container(fw, project_label, container_type, container_id):
    """
    Figures out what container_type and container_id should be if not given
    """
    cid = ctype = None
    if container_type and container_id:
        # Download single container
        cid = container_id
        ctype = container_type
    else:
        if bool(container_id) != bool(container_type):
            logger.error('Did not provide all options necessary to download single container')
            raise BIDSExportError('Did not provide all options necessary to download single container')
        elif not project_label:
            logger.error('Project label information not provided')
            raise BIDSExportError('Project label information not provided')
        # Get project Id from label
        cid = utils.validate_project_label(fw, project_label)
        ctype = 'project'
    return ctype, cid

def export_bids(fw, bids_dir, project_label, subjects=None, sessions=None, folders=None, replace=False,
        dry_run=False, container_type=None, container_id=None, source_data=False, validate=True):

    ### Prep
    # Check directory name - ensure it exists
    validate_dirname(bids_dir)

    # Check that container args are valid
    ctype, cid = determine_container(fw, project_label, container_type, container_id)

    ### Download BIDS project
    download_bids_dir(fw, cid, ctype, bids_dir,
            src_data=source_data, dry_run=dry_run, replace=replace,
            subjects=subjects, sessions=sessions, folders=folders)

    # Validate the downloaded directory
    #   Go one more step into the hierarchy to pass to the validator...
    if validate and not dry_run:
        utils.validate_bids(bids_dir)

def main():
    ### Read in arguments
    parser = argparse.ArgumentParser(description='BIDS Directory Export')
    parser.add_argument('--bids-dir', dest='bids_dir', action='store',
            required=True, help='Name of directory in which to download BIDS hierarchy. \
                    NOTE: Directory must be empty.')
    parser.add_argument('--api-key', dest='api_key', action='store',
            required=True, help='API key')
    parser.add_argument('--source-data', dest='source_data', action='store_true',
            default=False, required=False, help='Include source data in BIDS export')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
            default=False, required=False, help='Don\'t actually export any data, just print what would be exported')
    parser.add_argument('--replace', dest='replace', action='store_true',
            default=False, required=False, help='Replace files if the modified timestamps do not match')
    parser.add_argument('--subject', dest='subjects', action='append', help='Limit export to the given subject')
    parser.add_argument('--session', dest='sessions', action='append', help='Limit export to the given session name')
    parser.add_argument('--folder', dest='folders', action='append', help='Limit export to the given folder. (e.g. func)')
    parser.add_argument('-p', dest='project_label', action='store',
            required=False, default=None, help='Project Label on Flywheel instance')
    parser.add_argument('--container-type', dest='container_type', action='store', required=False, default=None,
            help='Download single container (acquisition|session|project) in BIDS format. Must provide --container-id.')
    parser.add_argument('--container-id', dest='container_id', action='store', required=False, default=None,
            help='Download single container in BIDS format. Must provide --container-type.')
    args = parser.parse_args()

    # Check API key - raises Error if key is invalid
    fw = flywheel.Flywheel(args.api_key)

    try:
        export_bids(fw, args.bids_dir, args.project_label, subjects=args.subjects, sessions=args.sessions, folders=args.folders, replace=args.replace,
                dry_run=args.dry_run, container_type=args.container_type, container_id=args.container_id, source_data=args.source_data)
    except utils.BIDSException as bids_exception:
        logger.error(bids_exception)
        sys.exit(bids_exception.status_code)

if __name__ == '__main__':
    main()

