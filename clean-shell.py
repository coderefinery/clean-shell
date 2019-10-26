#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import unshare

parser = argparse.ArgumentParser()
parser.add_argument('--persist', action='store_true',
                    help="Don't make a temporary copy of the default files, "
                         "but bind-mount to the original copy.  The "
                         "originals will be modified in place.")
parser.add_argument('--verbose', '-v', action='store_true',
                    help="Be verbose.")
args = parser.parse_args()


FILES = {
    '~/.bashrc',
    '~/.gitconfig',
    '~/.gitignore',
    '~/.ssh/',
    }

def copy(src, dest):
    """Copy either file or directory

    Because shutil.copytree annoyingl assumes a directory and fails if
    not.
    """
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    else:
        shutil.copy(src, dest)


cs_path = Path(os.path.dirname(__file__))
default_path = cs_path / 'defaults'
local_path = Path('~/.clean-shell').expanduser()

# Add any extra files/directories from ~/.clean-shell to the list of
# stuff to be replaced.
if local_path.exists():
    for p in local_path.iterdir():
        name = p.name
        if name.endswith('~') or name.endswith('#'):
            continue
        name = '~/' + name
        if p.is_dir():
            name = name + '/'
        FILES.add(name)


UID = os.getuid()
GID = os.getgid()

tmpdir = tempfile.TemporaryDirectory(prefix='clean-shell-')
tmp_path = Path(tmpdir.name)

# Check if it is allowed for normal users:
unpriv_path = Path('/proc/sys/kernel/unprivileged_userns_clone')
if unpriv_path.exists() and unpriv_path.read_text()[0] == '0':
    print("Must enable user namespace clone: sudo su -c 'echo 1 > /proc/sys/kernel/unprivileged_userns_clone'")
    exit(1)

#print('phase 1')
unshare.unshare(unshare.CLONE_NEWNS
                |unshare.CLONE_NEWUSER)
open("/proc/self/setgroups", "w").write('deny')
open("/proc/self/uid_map", 'w').write('0 %s 1'%UID)
open("/proc/self/gid_map", 'w').write('0 %s 1'%GID)

#print('uid:', os.getuid())


# Rebind all files
for dest in FILES:
    dest = os.path.expanduser(dest)
    is_dir = dest.endswith('/')
    dest = Path(dest)
    basename = dest.name  # if dir, pathlib.Path removes trailing slash

    # Take values from ~/.clean-shell/
    if (local_path / basename).exists():
        src = local_path / basename
        if not args.persist:
            copy(str(src), str(tmp_path/basename))
            src = (tmp_path/basename)
    # Take values from DIRNAME/defaults/   (DIRNAME=dir of this script)
    elif (default_path / basename).exists():
        src = default_path / basename
        if not args.persist:
            copy(str(src), str(tmp_path/basename))
            src = (tmp_path/basename)
    # Make a new empty file or directory
    else:
        src = (tmp_path / basename)
        if is_dir:
            src.mkdir()
        else:
            src.touch()

    # Mount will fail it if doesn't exist, if we touch it first then it
    # will persist after we are done.  Better solution to this later?
    if not dest.exists():
        print("Ignoring non-existing file %s"%str(dest))
        continue
    if args.verbose:
        print("%s --> %s"%(str(src), str(dest)))

    subprocess.check_call(['mount', '--bind', str(src), str(dest)])

#print('phase 2')
unshare.unshare(unshare.CLONE_NEWUSER)
open("/proc/self/setgroups", "w").write('deny')
open("/proc/self/uid_map", 'w').write('%s 0 1'%UID)
open("/proc/self/gid_map", 'w').write('%s 0 1'%UID)

#print("executing bash")
# Spawn instead of exec, so that
shell = os.environ.get('SHELL', 'bash')
os.spawnv(os.P_WAIT, shell, [shell])
