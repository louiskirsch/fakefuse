#!/usr/bin/env python3

import sys
import errno
from time import time
from fuse import FUSE, FuseOSError, Operations
from typing import Sequence, Dict, Any
from stat import S_IFDIR


class MyFileSystem(Operations):

    def __init__(self, paths):
        self.files = self.expand_paths_to_dict(paths)

    def expand_paths_to_dict(self, paths: Sequence[str]) -> Dict[str, Any]:
        # Convert a list of paths to a dictionary
        # Example: ['a/b', 'a/c'] -> {'a': {'b': {}, 'c': {}}}
        files = {}
        for path in paths:
            parts = path.split('/')
            current = files
            for part in parts:
                if part == '.':
                    continue
                if part not in current:
                    current[part] = {}
                current = current[part]
        return files

    # Filesystem methods
    # ==================

    def getattr(self, path, fh=None):
        # Return file/directory attributes
        # (st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime)
        # Raise FuseOSError(errno.ENOENT) if the path doesn't exist
        parts = path.split('/')
        parts = [part for part in parts if part]
        current = self.files

        for part in parts:
            if part not in current:
                raise FuseOSError(errno.ENOENT)
            current = current[part]

        is_dir = len(current) > 0
        now = time()

        return {
            'st_mode': (S_IFDIR | 0o755),
            'st_nlink': 2 if is_dir else 1,
            'st_size': 0,
            'st_ctime': now,
            'st_mtime': now,
            'st_atime': now,
        }

    def readdir(self, path, fh):
        # Return a list of directory entries as (name, attributes, type) tuples
        # type is either DT_DIR for directories or DT_REG for files
        parts = path.split('/')
        parts = [part for part in parts if part]
        current = self.files

        for part in parts:
            if part not in current:
                raise FuseOSError(errno.ENOENT)
            current = current[part]

        return ['.', '..'] + list(current.keys())

    def mkdir(self, path, mode):
        # Create a new directory at path with the given mode
        # Raise FuseOSError(errno.EEXIST) if the path already exists

        # Raise error because it is not implemented
        raise FuseOSError(errno.ENOSYS)

    def rmdir(self, path):
        # Remove the directory at path
        # Raise FuseOSError(errno.ENOENT) if the path doesn't exist
        # Raise FuseOSError(errno.ENOTEMPTY) if the directory is not empty
        raise FuseOSError(errno.ENOSYS)

    def create(self, path, mode, fi=None):
        # Create a new file at path with the given mode
        # Return a file handle
        raise FuseOSError(errno.ENOSYS)

    def open(self, path, flags):
        # Open the file at path with the given flags
        # Return a file handle
        raise FuseOSError(errno.ENOSYS)

    def read(self, path, length, offset, fh):
        # Read length bytes from the file at path starting at offset
        # Return a byte string of the read data
        raise FuseOSError(errno.ENOSYS)

    def write(self, path, data, offset, fh):
        # Write data to the file at path starting at offset
        # Return the number of bytes written
        raise FuseOSError(errno.ENOSYS)

    def truncate(self, path, length, fh=None):
        # Truncate the file at path to length bytes
        raise FuseOSError(errno.ENOSYS)

    def unlink(self, path):
        # Remove the file at path
        raise FuseOSError(errno.ENOSYS)

    def rename(self, old, new):
        # Rename the file or directory at old to new
        raise FuseOSError(errno.ENOSYS)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {} <mountpoint>'.format(sys.argv[0]))
        sys.exit(1)

    mountpoint = sys.argv[1]

    # Read paths from stdin
    paths = []
    for line in sys.stdin:
        paths.append(line.strip())

    fuse = FUSE(MyFileSystem(paths), mountpoint, nothreads=True, foreground=True)
