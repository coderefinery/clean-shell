Clean shell environment for demos
=================================

You are giving demos on your computer, but you have heavily customized
``.bashrc``, ``.gitconfig``, etc.  You don't want to have to move
these out of the way every time.  Linux namespaces to the rescue!
``clean-shell`` creates a new mount namespace, which can replace the
values of these config files with empty (or minimal) defaults.  That
shell, and any subprocesses, will experience this clean environment.

Files cleaned by default: ``.bashrc``, ``~/.ssh/``, and
``~/.gitconfig``, ``~/.gitignore``.  Furthermore, anything in
``~/.clean-shell/`` will be replaced (the basename there will have
``~/`` appended to it) also.  Non-existing original files will be
ignored (thus, you might make them in the subshell).

Currently only supports Linux, because ``unshare`` only works there.
But perhaps other operating systems have they own way of doing
namespaces?  Contributions welcome.



Installation
------------
``clean-shell.py`` is a single-file Python, no installation needed.
Requires Python>=3.4.

Dependencies: ``unshare`` (``pip install --user unshare``).  This is a
thin wrapper around the ``unshare`` Linux system call.

Unprivileged users need to be able to use namespaces.  You can make
this so with ``sudo bash -c 'echo 1 >
/proc/sys/kernel/unprivileged_userns_clone'``.  I'm currently unclear
if this is only disabled in Debian-like Linuxes, or if this is always
disabled by default for normal users.  If it is disabled by default,
this really is much less useful.  Expert advice would be welcome here.



Invocation
----------

* ``-v`` runs in verbose mode (print all files being altered)
* ``--persist`` will bind-mount the original template files, so that
  any modifications are persisted across sessions.  Perhaps useful for
  recurring demos where you are defining your own aliases and so on.
  May have currently-unknown interactions with the different
  directories.



"Default" files
---------------
The first of these values is taken as the replacement value for each
file:

- ``~/.clean-shell/BASENAME``
- ``DIRNAME/defaults/BASENAME``, where ``DIRNAME`` is the directory
  containing ``clean-shell.py``.
- A empty file, or an empty directory if the path to be replaced ends
  in ``/``.



Persistent replacement files
----------------------------

Sometimes, you don't want to completely reset your ``.bashrc``
etc. each time you run clean-shell.  You can handle that, too.

You can ::
   mkdir ~/.csdefaults
   touch ~/.csdefaults/.bashrc
   touch ~/.csdefaults/.gitconfig

The files in ``~/.csdefault/`` are bind-mounted in, and if you use
``--persist`` then any changes inside get persisted to this location.



Development and maintenance
---------------------------
Status: Alpha; improvements, including breaking improvements, are
welcome.

Editor: Richard Darst, Aalto University.
