# This is a file to just to include everything you need to not to worry much about it
# from base_utils import *
# logger = init_log(out_file = 'some_log.log', stderr = False)

import logging, sys, os


LOGGING_LEVELS = {
    'debug' : logging.DEBUG,
    'info' : logging.INFO,
    'warning' : logging.WARNING,
    'error' : logging.ERROR,
    'critical' : logging.CRITICAL
}

def init_log(out_file = None, stderr = False, level = logging.DEBUG, stderr_level = logging.DEBUG, file_level = logging.DEBUG):
    all_loggers = [logging.getLogger()]

    log_formatter = logging.Formatter('%(asctime)-15s %(levelname)10s %(message)s')

    if stderr:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(log_formatter)
        stderr_handler.setLevel(stderr_level)

    if out_file:
        if os.path.exists(out_file):
            os.remove(out_file)
        file_handler = logging.FileHandler(out_file)
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(file_level)

    for logger in all_loggers:
        logger.handlers = []
        logger.setLevel(level)

        if stderr:
            logger.addHandler(stderr_handler)

        if out_file:
            logger.addHandler(file_handler)

    main_logger = all_loggers[0]
    main_logger.info('Logger initialized')
    return main_logger

def ensure_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    return s
