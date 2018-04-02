#!/usr/bin/env python
# Condensed version of nsls-ii's build scripts
import argparse
import shutil
from pathlib import Path
from subprocess import check_output

import binstar_client

PACKAGES = ['epics-base']
PYTHON = ['3.6']
NUMPY = ['1.13']
#PACKAGES = ['epics-base', 'pcaspy', 'pyca', 'pydm', 'pyepics']
#PYTHON = ['3.5', '3.6']
#NUMPY = ['1.11', '1.12', '1.13', '1.14']
BUILD_DIR = str(Path(__file__).parent / 'conda-bld')


def get_uploaded_files(client, channel):
    print('Checking uploaded files')
    files = set()
    for fl in client.show_channel('main', channel)['files']:
        files.add(fl['basename'])
    return files


def build_args(package, channel, py=None, np=None, dev=False):
    args = ['conda', 'build', package,
            '-c', channel, '-c', 'defaults', '-c', 'conda-forge',
            '--override', '--output-folder', BUILD_DIR]
    if py is not None:
        args.extend(['--python', py])
    if np is not None:
        args.extend(['--numpy', np])
    return args


def check_filename(package, channel, py=None, np=None):
    print('Checking build filename')
    args = build_args(package, channel, py=py, np=np) + ['--output']
    print(' '.join(args))
    output = check_output(args, universal_newlines=True)
    print(output)
    return output


def build(package, channel, py=None, np=None):
    print('Building {}'.format(package))
    args = build_args(package, channel, py=py, np=np)
    print(' '.join(args))
    output = check_output(args, universal_newlines=True)
    print(output)
    return output


def upload(client, channel, filename):
    print('Uploading {}'.format(filename))
    args = ['anaconda', '-t', client.token, 'upload', '-u', channel, filename]
    print(' '.join(args))
    output = check_output(args, universal_newlines=True)
    print(output)
    return output


def build_all():
    print('Running build script')
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', action='store', required=True)
    parser.add_argument('--token', action='store', required=True)
    args = parser.parse_args()

    channel = args.channel
    token = args.token

    client = binstar_client.Binstar(token=token)
    files = get_uploaded_files(client, channel)

    try:
        shutil.rmtree(BUILD_DIR)
    except Exception:
        pass
    build_path = Path(BUILD_DIR)
    build_path.mkdir()

    for package in PACKAGES:
        print('Check if we need to build {}'.format(package))
        for py in PYTHON:
            for np in NUMPY:
                print('Checking python={}, numpy={}'.format(py, np))
                full_path = check_filename(package, channel, py=py, np=np)
                short_path = '/'.join(full_path.split('/')[-2:])
                if short_path in files:
                    print('Skip {}'.format(short_path))
                else:
                    files.add(short_path)
                    build(package, channel, py=py, np=np)
                    upload(client, channel, full_path)


if __name__ == '__main__':
    build_all()
