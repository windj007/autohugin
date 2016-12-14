#!/usr/bin/env python

import argh, logging, resource

from autohugin.detect import group_images_and_make_config
from autohugin.base_utils import init_log
from autohugin.hugin import process_panos_default, stitch_projects, \
    scale_panos, print_not_stitched_projects

parser = argh.ArghParser()
parser.add_argument('-m',
                    type = int,
                    default = 3 * 1024 * 1024 * 1024,
                    help = 'How much virtual memory to allow to consume')
parser.add_commands([group_images_and_make_config,
                     process_panos_default,
                     stitch_projects,
                     scale_panos,
                     print_not_stitched_projects])


init_log(stderr = True, level = logging.INFO)


if __name__ == '__main__':
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (args.m, args.m))

    parser.dispatch()
