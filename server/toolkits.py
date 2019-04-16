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

    parser.add_argument('-t', '--test',
                        dest='config',
                        action='store_const',
                        const='testing',
                        help='Manually start debug as testing config.')

    parser.add_argument('-p', '--production',
                        dest='config',
                        action='store_const',
                        const='production',
                        help='Manually start debug as production config.')

    args, unknown = parser.parse_known_args()

    config = args.config or 'default'

    if args.command == 'index':
        generate_index(config)
    elif args.command in ['migration', 'migrate', 'mg']:
        migration(config)
    else:
        print '!! This command is not supported.'
