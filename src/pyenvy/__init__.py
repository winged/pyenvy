#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

"""
PyEnvy is a simple tool to help using the right virtualenv in all cases.

It provides a way to set a preferred virtualenv for every python script,
and also provides a way to force-disable an active virtualenv if you're
running a system script that may be incompatible with your virtualenv.

The basic principle is that you have an external config file for each
script that defines a path to a virtualenv to be used. PyEnvy then
automatically loads that virtualenv upon script start.

Usage is pretty simple: At the beginning of your script, put the
following lines:

    >>> import pyenvy
    >>> pyenvy.init()

What happens behind the scene is best explained by an example. Say we
have a script in /usr/local/bin/envy_sample.py:

    >>> #!/usr/bin/env python
    >>> import pyenvy
    >>> pyenvy.init()

PyEnvy will then first look at a .pyenv file in the same place as the
script by appending .pyenv to the script's filename. In our example, this
would be /usr/local/bin/envy_sample.py.pyenv.

If the file exists, it is expected that this file contains a single line
that points to the base dir of a virtualenv. If this is the case, the
virtualenv is loaded and execution continues. If the path given does not
exist, an exception is thrown and execution aborts.  If however the file
is empty, then this regarded as explicitly stating "do not use a virtualenv
for this script". In that case, any existing virtualenvs will be disabled
before commencing execution.

Instead of putting .pyenv files all in the same place as the scripts
themselves, you can also put them in /etc/pyenvy. The name resolution
for a pyenv file is as follows:

1) Look in the same folder as the script being executed. If the script's
   filename is for example foo.py, it will first look for foo.py.pyenv in
   the same folder.
2) Lookup commences in /etc/pyenvy. If the absolute path to the script
   being executed is also found relative to /etc/pyenvy, it is
   used instead.  Example: /usr/local/bin/sample.py will look for
   /etc/pyenvy/usr/local/bin/sample.py.pyenv
3) If this does not work, we fall back to looking up the basename of the
   script. Using the same sample.py from above, the next lookup would
   be /etc/pyenvy/sample.py.pyenv.

If no pyenv file has been found during those steps, we assume that
no virtualenv is required, and therefore forcibly disable a possibly active
virtualenv.

"""

# Copyright (c) 2013, Adfinis SyGroup AG
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Adfinis SyGroup AG nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS";
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Adfinis SyGroup AG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# System Imports
import os.path


SUFFIX     = '.pyenv'
PYENVY_ETC = [
    '/etc/pyenvy',
    # TODO: directories for Windows, OSX, ...
]

# Exportable symbols
__all__ = [
    'init'
]


def _lookup_envfile(script):
    # make sure we have an absolute path
    script = os.path.abspath(script)

    envfile = script + SUFFIX

    # Step 1: same directory as script itself
    if os.path.lexists(envfile):
        return envfile

    relpath = envfile[1:]  # Strip off leading slash

    # Look in system-wide config dir
    actual_configdirs = [
        d
        for d in PYENVY_ETC
        if os.path.isdir(d)
    ]
    for config_dir in actual_configdirs:
        # Step 2: subdir of the system-wide config dir
        check_file = os.path.join(config_dir, relpath)
        if os.path.lexists(check_file):
            return check_file

        # Step 3: look in system-wide config dir, but only the basename.
        check_file = os.path.join(config_dir, os.path.basename(relpath))
        if os.path.lexists(check_file):
            return check_file

    # If no file has been found until now, there is no pyenv file.
    # Return None to signal it.
    return None


def _env_from_file(envfile):

    try:
        with open(envfile, 'r') as fh:
            path_line = fh.readline()
        return path_line.strip()
    except:
        return None


def _disable_virtualenv():
    if 'VIRTUALENV' in os.environ:
        print("TODO: disable virtualenv")
    else:
        print("NOP: Disabling non-existant virtualenv")


def _enable_virtualenv(path):
    envloader = os.path.join(path, 'bin/activate_this.py')

    if os.path.isfile(envloader):
        print("INFO: Loading env %s" % path)
        _do_execfile(envloader)

    else:
        print("ERROR: virtualenv configured, but %s seems broken" % path)


def _do_execfile(envloader):
    if 'execfile' in dir(__builtins__):
        func = getattr(__builtins__, 'execfile')
        return func(
            envloader,
            dict(__file__=envloader)
        )

    else:
        # Python 3
        exec(
            compile(open(envloader).read(), envloader, 'exec'),
            dict(__file__=envloader)
        )


def init():
    import sys
    script = os.path.abspath(sys.argv[0])

    env_file = _lookup_envfile(script)
    if env_file is None:
        return _disable_virtualenv()

    else:
        env_dir = _env_from_file(env_file)
        if env_dir is None:
            return _disable_virtualenv()

        return _enable_virtualenv(env_dir)
