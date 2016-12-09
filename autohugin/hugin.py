import subprocess, logging, traceback

from .config import BatchPanoConfig

logger = logging.getLogger(__name__)


DEFAULT_PTO_EXECUTABLE = 'pto_gen'
DEFAULT_BATCHER_EXECUTABLE = 'PTBatcherGUI'

def create_basic_project(input_files, project_fname, pto_executable = DEFAULT_PTO_EXECUTABLE):
    subprocess.check_call([pto_executable,
                           '-o',
                           project_fname] + list(input_files))

def add_project_to_batcher(project_fname, batcher_executable = DEFAULT_BATCHER_EXECUTABLE):
    subprocess.check_call([batcher_executable, '-a', project_fname])


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
            logger.info('Submitting %s to queue' % pano['project_filename'])
            add_project_to_batcher(pano['project_filename'],
                                   batcher_executable = batcher_executable)
        except subprocess.CalledProcessError:
            logger.warn('Could not process %s due to\n%s' % (pano['project_filename'],
                                                             traceback.format_exc()))
