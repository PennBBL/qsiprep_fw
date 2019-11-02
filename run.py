#!/usr/local/miniconda/bin/python
import sys
import logging
import shutil
from zipfile import ZipFile
from unittest import mock
import argparse
from pathlib import PosixPath
from fw_heudiconv.cli import export
import flywheel
from qsiprep.cli import run as qsiprep_run

# logging stuff
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('qsiprep-gear')
logger.info("=======: QSIPrep :=======")


# Gather variables that will be shared across functions
with flywheel.GearContext() as context:
    # Setup basic logging
    context.init_logging()
    # Log the configuration for this job
    # context.log_config()
    config = context.config
    builtin_recon = config.get('recon_builtin')
    recon_spec = builtin_recon if builtin_recon else \
        context.get_input_path('recon_spec')
    ignore = config.get('ignore', '').split()
    output_space = config.get('output_space', '').split()
    analysis_id = context.destination['id']
    gear_output_dir = PosixPath(context.output_dir)
    output_root = gear_output_dir / analysis_id
    output_dir = output_root / "derivatives"
    working_dir = output_root / "work"
    bids_dir = output_root / "BIDS"
    bids_root = bids_dir / 'bids_dataset'
    # Get relevant container objects
    fw = flywheel.Client(context.get_input('api_key')['key'])
    analysis_container = fw.get(analysis_id)
    project_container = fw.get(analysis_container.parents['project'])
    session_container = fw.get(analysis_container.parent['id'])
    subject_container = fw.get(session_container.parents['subject'])

    project_label = project_container.label
    extra_t1 = context.get_input('t1_anatomy')
    extra_t1_path = None if extra_t1 is None else \
        PosixPath(context.get_input_path('t1_anatomy'))
    extra_t2 = context.get_input('t2_anatomy')
    extra_t2_path = None if extra_t2 is None else \
        PosixPath(context.get_input_path('t2_anatomy'))
    use_all_sessions = config.get('use_all_sessions', False)

    # output zips
    html_zipfile = gear_output_dir / (analysis_id + "_qsiprep_html.zip")
    derivatives_zipfile = gear_output_dir / (analysis_id + "_qsiprep_derivatives.zip")
    debug_derivatives_zipfile = gear_output_dir / (
        analysis_id + "_debug_qsiprep_derivatives.zip")
    working_dir_zipfile = gear_output_dir / (analysis_id + "_qsiprep_workdir.zip")
    errorlog_zipfile = gear_output_dir / (analysis_id + "_qsiprep_errorlog.zip")


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
            bids_dir=bids_root,
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
            fs_license_file=PosixPath(context.get_input_path('freesurfer_license')),
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
            stop_on_first_crash=True,
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
        qsiprep_run.main()


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
    nifti_bids_path = bids_root / nifti.info['BIDS']['Path']
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
    bids_root.parent.mkdir(parents=True, exist_ok=True)
    downloads = export.gather_bids(fw, project_label, subjects, sessions)
    export.download_bids(fw, downloads, str(bids_dir.resolve()), dry_run=False)

    # Download the extra T1w or T2w
    if extra_t1 is not None:
        get_external_bids(extra_t1, extra_t1_path)
    if extra_t2 is not None:
        get_external_bids(extra_t2, extra_t2_path)

    dwi_files = [fname for fname in bids_root.glob("**/*") if "dwi/" in str(fname)]
    if not len(dwi_files):
        raise Exception("No DWI files found in %s" % bids_root)


def create_html_zip():
    html_root = output_dir / "qsiprep"
    html_files = list(html_root.glob("sub-*html"))
    if not html_files:
        logger.warning("No html files found!")
        return
    html_figures = list(html_root.glob("*/figures/*"))
    html_outputs = html_files + html_figures
    with ZipFile(str(html_zipfile), "w") as zipf:
        for html_output in html_outputs:
            zipf.write(str(html_output),
                       str(html_output.relative_to(html_root)))
    assert html_zipfile.exists()


def create_derivatives_zip(failed):
    output_fname = debug_derivatives_zipfile if failed else derivatives_zipfile
    derivatives_files = list(output_dir.glob("**/*"))
    with ZipFile(str(output_fname), "w") as zipf:
        for derivative_f in derivatives_files:
            zipf.write(str(derivative_f),
                       str(derivative_f.relative_to(output_dir)))


def create_workingdir_zip():
    working_files = list(working_dir.glob("**/*"))
    with ZipFile(str(working_dir_zipfile), "w") as zipf:
        for working_f in working_files:
            zipf.write(str(working_f),
                       str(working_f.relative_to(working_dir)))


def upload_results(failed):
    """Perform cleanup and upload any requested outputs.
    """
    upload_derivatives = not failed or \
        (failed and config.get('save_partial_outputs', False))
    try:
        create_html_zip()
    except Exception as e:
        logger.warning("Unable to create html zip files")
        print(e)

    if upload_derivatives:
        logger.info("Zipping QSIPrep derivatives")

        try:
            create_derivatives_zip(failed=failed)
        except Exception as e:
            logger.warning("Unable to create derivatives archive")
            print(e)

    if config.get('save_intermediate_work', False):
        try:
            create_workingdir_zip()
        except Exception as e:
            logger.warning("Unable to create working directory archive")
            print(e)

    logger.info("Cleaning up working directory")
    shutil.rmtree(str(output_root))

def main():

    OK = True
    try:
        fw_heudiconv_download()
    except Exception as e:
        logger.warning("Critical error while trying to download BIDS data.")
        print(e)
        upload_results(failed=True)
        OK = False

    try:
        if OK:
            run_qsiprep()
    except Exception as e:
        logger.warning("Critical error while trying to run QSIPrep.")
        print(e)
        upload_results(failed=True)
        OK = False

    upload_results(failed=not OK)
    sys.exit(0)


if __name__ == '__main__':
    main()
