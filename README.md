PyEnvy - a python virtualenv autoloader
=======================================

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
