import subprocess32 as subprocess, logging, traceback, os

from .config import BatchPanoConfig
from .base_utils import ensure_utf8

logger = logging.getLogger(__name__)


DEFAULT_PTO_EXECUTABLE = 'pto_gen'
DEFAULT_BATCHER_EXECUTABLE = 'PTBatcherGUI'

def create_basic_project(input_files, project_fname, pto_executable = DEFAULT_PTO_EXECUTABLE):
    subprocess.check_call([pto_executable,
                           '-o',
                           project_fname] + list(input_files))

def process_project(project_fname):
    subprocess.check_call(('cpfind', '-o', project_fname, '--multirow', '--celeste', project_fname))
    subprocess.check_call(('cpclean', '-o', project_fname, project_fname))
    subprocess.check_call(('linefind', '-o', project_fname, project_fname))
    subprocess.check_call(('autooptimiser', '-a', '-m', '-l', '-s', '-o', project_fname, project_fname))
    subprocess.check_call(('pano_modify', '-c', '--ldr-file=JPG', '--canvas=AUTO', '--crop=AUTO', '-o', project_fname, project_fname))


def scale_pano(project_fname, size):
    logger.info('Scale %s' % project_fname)
    subprocess.check_call(('pano_modify', '--canvas=%s' % size, '-o', project_fname, project_fname))


def scale_panos(size, *projects):
    for proj in projects:
        scale_pano(proj, size)


OUTPUT_SUFFICES = ('.jpg', '_fused.jpg', '.tif')
def try_get_output_filename(prefix):
    for suffix in OUTPUT_SUFFICES:
        fname = prefix + suffix
        if os.path.isfile(fname):
            return fname
    return None


def get_not_stitched_projects(*project_fnames):
    for fname in project_fnames:
        if try_get_output_filename(os.path.splitext(fname)[0]) is None:
            yield fname


def print_not_stitched_projects(*project_fnames):
    for fname in get_not_stitched_projects(*project_fnames):
        print ensure_utf8(fname)


def first_is_newer(first, second):
    return os.path.getmtime(first) > os.path.getmtime(second)


def stitch_project(project_fname, force = False, timeout = 10 * 60):
    prefix = os.path.splitext(project_fname)[0]
    res_fname = try_get_output_filename(prefix)
    if res_fname and first_is_newer(res_fname, project_fname) and not force:
        logger.info('Skipping %s, because newer result exists and not forced' % project_fname)
        return
    subprocess.check_call(('hugin_stitch_project',
                           '-w',
                           '-o', prefix,
                           project_fname),
                          timeout = timeout)


def process_panos_default(config_file,
                          pto_executable = DEFAULT_PTO_EXECUTABLE,
                          batcher_executable = DEFAULT_BATCHER_EXECUTABLE):
    config = BatchPanoConfig.load(config_file)
    for pano in config.panos:
        try:
            logger.info('Creating %s' % pano['project_filename'])
            create_basic_project(pano['source_files'],
                                 pano['project_filename'],
                                 pto_executable = pto_executable)
            logger.info('Processing %s' % pano['project_filename'])
            process_project(pano['project_filename'])
        except subprocess.CalledProcessError:
            logger.warn('Could not process %s due to\n%s' % (pano['project_filename'],
                                                             traceback.format_exc()))


def stitch_projects(force = False, timeout = 10 * 60, *project_files):
    for fname in project_files:
        try:
            logger.info('Stitching %s' % fname)
            stitch_project(fname,
                           force = force,
                           timeout = timeout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            logger.warn('Could not stitch %s due to\n%s' % (fname,
                                                            traceback.format_exc()))
