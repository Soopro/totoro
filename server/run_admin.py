# coding=utf-8
from __future__ import absolute_import

from admin.application import create_app
import argparse

parser = argparse.ArgumentParser(description='Options of start server.')

parser.add_argument('-t', '--test',
                    dest='server_mode',
                    action='store_const',
                    const='testing',
                    help='Manually start debug as testing config.')

parser.add_argument('-p', '--production',
                    dest='server_mode',
                    action='store_const',
                    const='production',
                    help='Manually start debug as production config.')

args, unknown = parser.parse_known_args()

app = create_app(args.server_mode or 'default')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9009, threaded=True)
