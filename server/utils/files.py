# coding=utf-8
from __future__ import absolute_import

from slugify import slugify
import datetime
import zipfile
import shutil
import hashlib
import requests
import urlparse
import uuid
import os


def head_file(src, secure=True):
    r = requests.head(src, timeout=5)
    r.encoding = 'utf-8'
    r.raise_for_status()
    headers = r.headers

    size = int(headers.get('content-length', 0))
    mimetype = headers.get('content-type')
    file_type = mimetype.split('/')[0]

    filename = os.path.basename(urlparse.urlparse(src).path)
    if secure:
        convert_ext_map = {'.jpe': '.jpg'}
        name, ext = os.path.splitext(filename)
        name = slugify(name)
        if len(name) <= 3:
            name += uuid.uuid4().hex[:12]
        ext = convert_ext_map.get(ext, ext)
        filename = name + ext
    return {
        'filename': filename,
        'size': size,
        'mimetype': mimetype,
        'type': file_type,
        'src': src,
        'headers': headers,
    }


def download_file(src, path, timeout=10, max_size=None,
                  allow_redirects=True):
    r = requests.get(src, timeout=timeout, stream=True,
                     allow_redirects=allow_redirects)
    r.raise_for_status()
    try:
        write_file(data=r.iter_content(1024), path=path, max_size=max_size)
    except Exception as e:
        raise e
    return path


def file_md5(fname):
    _hash = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            _hash.update(chunk)
    return _hash.hexdigest()


def unzip(file_path, to_path):
    with zipfile.ZipFile(file_path, 'r') as z:
        z.extractall(to_path)


def modification_date(filepath):
    """
    get the standard str format of utc datetime
    of the given file's last-modified
    """
    if not filepath:
        return ''
    t = os.path.getmtime(filepath)
    return datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')


def modification_timestamp(filepath):
    return os.path.getmtime(filepath)


def zipdir(zipfile_location, source_dir):
    """
    package a directory into a zip file
    :param zipfile_location: the location of output zipfile
    :param source_dir: the direcotry need to be compressed
    :return:
    """
    with zipfile.ZipFile(zipfile_location, 'w', zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                arcname = os.path.relpath(os.path.join(root, file),
                                          source_dir)
                zip.write(os.path.join(root, file), arcname)


# folders
def remove_dirs(*folders):
    for folder in folders:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
    return folders


def ensure_dirs(*folders):
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)
    return folders


# file
def write_file(data, path, max_size=0):
    if max_size < 0:
        max_size = 0
    if isinstance(data, basestring):
        with open(path, 'wb') as f:
            if max_size and len(data) > max_size:
                f.write(data)
    else:
        with open(path, 'wb') as f:
            size = 0
            for chunk in data:
                size += len(chunk)
                if max_size and size > max_size:
                    raise IOError('file too large')
                f.write(chunk)
    return path
