# coding=utf-8
from __future__ import absolute_import
from toolkits import *

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Options of starting toolkits.')

    parser.add_argument(dest='command',
                        action='store',
                        help='Run toolkits command.')

    parser.add_argument('--config',
                        dest='config',
                        action='store',
                        type=str,
                        nargs='?',
                        default='default',
                        const='default',
                        help='Manually start with specified config.')

    args, unknown = parser.parse_known_args()

    config = args.config or 'default'

    if args.command == ['index', 'indexes']:
        generate_index(config)
    elif args.command in ['migration', 'migrate', 'mg']:
        migration(config)
    else:
        print '!! This command is not supported.'
