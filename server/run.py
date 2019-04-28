# coding=utf-8
from __future__ import absolute_import

from application import create_app
import argparse

parser = argparse.ArgumentParser(description='Options of start server.')

parser.add_argument('--config',
                    dest='config',
                    action='store',
                    type=str,
                    nargs='?',
                    default='default',
                    const='default',
                    help='Manually start with specified config.')

parser.add_argument('--host',
                    dest='server_host',
                    action='store',
                    type=str,
                    nargs='?',
                    default='0.0.0.0',
                    const='0.0.0.0',
                    help='Manually start debug with host.')

args, unknown = parser.parse_known_args()

app = create_app(args.config)
host = args.server_host

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=9000, host=host)
