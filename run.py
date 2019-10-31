from qsiprep.cli import run as qsiprep_run
from unittest import mock
import argparse
import flywheel

def args_from_flywheel():
    """Create a argparse.Namespace with gear options in it."""
    with flywheel.GearContext() as context:
        # Setup basic logging
        context.init_logging()

        # Log the configuration for this job
        context.log_config()
        config = context.config
        args = Namespace(
            acquisition_type=None,
            analysis_level='participant',
            anat_only=False,
            b0_motion_corr_to=config.get('b0_motion_corr_to', 'iterative'),
            b0_threshold=config.get(100,
            b0_to_t1w_transform='Rigid',
            bids_dir=PosixPath('.'),
            boilerplate=False,
            combine_all_dwis=False,
            denoise_before_combining=False,
            do_reconall=False,
            dwi_denoise_window=5,
            eddy_config=None,
            fmap_bspline=False,
            fmap_no_demean=True,
            force_spatial_normalization=False,
            force_syn=False,
            fs_license_file=None,
            hmc_model='eddy',
            hmc_transform='Affine',
            ignore=[],
            impute_slice_threshold=0,
            intramodal_template_iters=0,
            intramodal_template_transform='BSplineSyN',
            longitudinal=False,
            low_mem=False,
            mem_mb=0,
            notrack=False,
            nthreads=None,
            omp_nthreads=0,
            output_dir=PosixPath('.'),
            output_resolution=0.5,
            output_space=['T1w'],
            participant_label=None,
            prefer_dedicated_fmaps=False,
            recon_input=None,
            recon_only=False,
            recon_spec=None,
            reports_only=False,
            resource_monitor=False,
            run_uuid=None,
            shoreline_iters=2,
            skip_bids_validation=False,
            skull_strip_fixed_seed=False,
            skull_strip_template='OASIS',
            sloppy=False,
            stop_on_first_crash=False,
            template='MNI152NLin2009cAsym',
            use_plugin=None,
            use_syn_sdc=False,
            verbose_count=0,
            work_dir=None,
            write_graph=False,
            write_local_bvecs=False)
    return args


def run_qsiprep():
    # Run monkey patched version of main()
    with mock.patch.object(
            argparse.ArgumentParser, 'parse_args', return_value=args_from_flywheel()):
        return qsiprep_run.main()
