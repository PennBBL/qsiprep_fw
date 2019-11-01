#!/usr/local/miniconda/bin/python
from qsiprep.cli import run as qsiprep_run
import logging
from unittest import mock
import argparse
import flywheel
from pathlib import PosixPath
from fw_heudiconv.cli import export
from fw_heudiconv.query import print_directory_tree

# logging stuff
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fw-heudiconv-gear')
logger.info("=======: fw-heudiconv starting up :=======")


# Gather variables that will be shared across functions
with flywheel.GearContext() as context:
    # Setup basic logging
    context.init_logging()
    # Log the configuration for this job
    context.log_config()
    config = context.config
    builtin_recon = config.get('recon_builtin')
    recon_spec = builtin_recon if builtin_recon else \
        context.get_input_path('recon_spec')
    ignore = config.get('ignore', '').split()
    output_space = config.get('output_space', '').split()
    analysis_id = context.destination['id']
    output_root = PosixPath(config.output_dir) / analysis_id
    output_dir = output_root / "derivatives"
    working_dir = output_root / "work"
    bids_dir = output_root / "BIDS"

    # Get relevant container objects
    fw = flywheel.Client(context.get_input('api_key')['key'])
    analysis_container = fw.get(analysis_id)
    project_container = fw.get(analysis_container.parents['project'])
    session_container = fw.get(analysis_container.parent['id'])
    subject_container = fw.get(session_container.parents['subject'])

    project_label = project_container.label
    extra_t1 = context.get_input('t1_anatomy')
    extra_t1_path = PosixPath(context.get_input_path('t1_anatomy'))
    extra_t2 = context.get_input('t2_anatomy')
    extra_t2_path = PosixPath(context.get_input_path('t2_anatomy'))
    use_all_sessions = config.get('use_all_sessions', False)


def args_from_flywheel():
    """Create a argparse.Namespace with gear options in it."""
    with flywheel.GearContext() as context:
        # Log the configuration for this job
        args = argparse.Namespace(
            acquisition_type=None,
            analysis_level='participant',
            anat_only=False,
            b0_motion_corr_to=config.get('b0_motion_corr_to', 'iterative'),
            b0_threshold=config.get('b0_threshold', 100),
            b0_to_t1w_transform='Rigid',
            bids_dir=bids_dir / 'bids_dataset',
            boilerplate=False,
            combine_all_dwis=config.get('combine_all_dwis', False),
            denoise_before_combining=config.get('denoise_before_combining', False),
            do_reconall=config.get('do_reconall', False),
            dwi_denoise_window=config.get('dwi_denoise_window', 5),
            eddy_config=context.get_input_path('eddy_config'),
            fmap_bspline=config.get('fmap_bspline', False),
            fmap_no_demean=config.get('fmap_no_demean', True),
            force_spatial_normalization=config.get('force_spatial_normalization', False),
            force_syn=config.get('force_syn', False),
            fs_license_file=context.get_input_path('freesurfer_license'),
            hmc_model=config.get('hmc_model', 'eddy'),
            hmc_transform=config.get('hmc_transform', 'Affine'),
            ignore=ignore,
            impute_slice_threshold=config.get('impute_slice_threshold', 0),
            intramodal_template_iters=config.get('intramodal_template_iters', 0),
            intramodal_template_transform=config.get('intramodal_template_transform',
                                                     'BSplineSyN'),
            longitudinal=config.get('longitudinal', False),
            low_mem=False,
            mem_mb=0,
            notrack=config.get('notrack', False),
            nthreads=None,
            omp_nthreads=0,
            output_dir=output_dir,
            output_resolution=config.get('output_resolution'),
            output_space=output_space,
            participant_label=None,
            prefer_dedicated_fmaps=config.get('prefer_dedicated_fmaps', False),
            recon_input=None,  # Handled by QSIRecon gear
            recon_only=False,
            recon_spec=recon_spec,
            reports_only=False,
            resource_monitor=False,
            run_uuid=analysis_id,
            shoreline_iters=config.get('shoreline_iters', 2),
            skip_bids_validation=config.get('skip_bids_validation', False),
            skull_strip_fixed_seed=config.get('skull_strip_fixed_seed', False),
            skull_strip_template=config.get('skull_strip_template', 'OASIS'),
            sloppy=config.get('sloppy', False),
            stop_on_first_crash=config.get('skull_strip_template', False),
            template=config.get('template', 'MNI152NLin2009cAsym'),
            use_plugin=config.get('use_plugin', None),
            use_syn_sdc=config.get('use_syn_sdc', False),
            verbose_count=2,
            work_dir=working_dir,
            write_graph=False,
            write_local_bvecs=config.get('write_local_bvecs', False)
        )
    return args


def run_qsiprep():
    # Run monkey patched version of main()
    with mock.patch.object(
            argparse.ArgumentParser, 'parse_args', return_value=args_from_flywheel()):
        return qsiprep_run.main()


def get_external_bids(scan_info, local_file):
    """Download an external T1 or T2 image.

    Query flywheel to find the correct acquisition and get its BIDS
    info. scan_info came from context.get_input('*_anatomy').
    """
    modality = scan_info['object']['modality']
    logger.info("Adding additional %s folder...", modality)
    external_acq = fw.get(scan_info['hierarchy']['id'])
    external_niftis = [f for f in external_acq.files if
                       f.name == scan_info['location']['name']]
    if not len(external_niftis) == 1:
        raise Exception("Unable to find location for extra %s" % modality)
    nifti = external_niftis[0]
    nifti_bids_path = bids_dir / "bids_dataset" / nifti.info['BIDS']['Path']
    json_bids_path = str(nifti_bids_path).replace(
        "nii.gz", ".json").replace(".nii", ".json")
    # Warn if overwriting: Should never happen on purpose
    if nifti_bids_path.exists():
        logger.warning("Overwriting current T1w image...")
    # Copy to / overwrite its place in BIDS
    local_file.replace(nifti_bids_path)

    # Download the sidecar
    export.download_sidecar(nifti.info, json_bids_path)
    assert PosixPath(json_bids_path).exists()
    assert nifti_bids_path.exists()


def fw_heudiconv_download():

    subjects = [subject_container.label]
    if not use_all_sessions:
        # find session object origin
        sessions = [session_container.label]
    else:
        sessions = None

    # Do the download!
    downloads = export.gather_bids(fw, project_label, subjects, sessions)
    export.download_bids(fw, downloads, str(bids_dir.resolve()), dry_run=False)

    # Download the extra T1w or T2w
    if extra_t1 is not None:
        get_external_bids(extra_t1, extra_t1_path)
    if extra_t2 is not None:
        get_external_bids(extra_t2, extra_t2_path)

    # Print your download
    print_directory_tree(str(bids_dir / 'bids_dataset'))
