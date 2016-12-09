#!/usr/bin/env python

import argh, logging

from autohugin.detect import group_images_and_make_config
from autohugin.base_utils import init_log
from autohugin.hugin import process_panos_default

parser = argh.ArghParser()
parser.add_commands([group_images_and_make_config,
                     process_panos_default])


init_log(stderr = True, level = logging.INFO)


if __name__ == '__main__':
    parser.dispatch()
