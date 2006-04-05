##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Project checkout setup script

$Id$
"""

import os
import sys
import shutil
import optparse
import ConfigParser
import urllib2

DEV_SECTION = 'development'
DEV_DEPENDS = 'depends'

def bootstrap(libdir, bindir):
    """Bootstrap our setuptools installation in the target directory."""

    # make sure ez_setup is available
    try:
        # check if we have ez_setup available
        import ez_setup
        
    except ImportError, e:
        # retrieve ez_setup.py from the interweb
        EZ_URL = "http://peak.telecommunity.com/dist/ez_setup.py"
        
        ez_filename = os.path.join(os.path.dirname(__file__), 'ez_setup.py')
        file(ez_filename, 'w').write(
            urllib2.urlopen(EZ_URL).read()
            )

        import ez_setup
        
    os.environ['PYTHONPATH'] = (os.environ.setdefault('PYTHONPATH', '')
                               + ":" + libdir)
    ez_setup.main(['--install-dir', libdir,
                   '--script-dir', bindir,
                   '-U', 'setuptools'])

def initSetupCfg(setup_file, template_file='setup.cfg.in'):
    """Check if the setup_file (setup.cfg) exists; if it doesn't, and
    setup.cfg.in does, copy setup.cfg.in to setup.cfg to serve as a
    template."""

    if not(os.path.exists(setup_file)) and os.path.exists(template_file):
        shutil.copyfile(template_file, setup_file)
        
def updateSetupCfg(setup_file, opts):
    """Update or create a setup.cfg (setup_file) for working on this
    project."""

    # initialize the setup file if necessary
    initSetupCfg(setup_file)
    
    # load the existing version
    setup_cfg = ConfigParser.ConfigParser()
    setup_cfg.read(setup_file)

    # make sure the sections we want exist
    if not(setup_cfg.has_section('easy_install')):
        setup_cfg.add_section('easy_install')

    if not(setup_cfg.has_section('egg_info')):
        setup_cfg.add_section('egg_info')
        
    # update lib dir
    if opts.libdir is None:
        # no libdir specified; check for one in setup.cfg
        if setup_cfg.has_option('easy_install', 'install-dir'):
            opts.libdir = setup_cfg.get('easy_install', 'install-dir')
        else:
            opts.libdir = os.path.abspath('./lib')

    setup_cfg.set('easy_install', 'install-dir', opts.libdir)

    # update bin dir
    if opts.bindir is None:
        # no bindir specified; check for one in setup.cfg
        if setup_cfg.has_option('easy_install', 'script-dir'):
            opts.bindir = setup_cfg.get('easy_install', 'script-dir')
        else:
            opts.bindir = os.path.abspath('./bin')

    setup_cfg.set('easy_install', 'script-dir', opts.bindir)
        
    # update site-dirs
    setup_cfg.set('easy_install', 'site-dirs', opts.libdir)
    
    # update find-links
    setup_cfg.set('easy_install', 'find-links', opts.finddirs)

    # update egg_info for development version
    if not setup_cfg.has_option('egg_info', 'tag_build'):
        setup_cfg.set('egg_info', 'tag_build', '.dev')

    if not setup_cfg.has_option('egg_info', 'tag_svn_revision'):
        setup_cfg.set('egg_info', 'tag_svn_revision', '1')

    # store the updated version
    setup_cfg.write(file(setup_file, 'w'))

def load_dev_deps(setup_file):
    global DEV_SECTION
    global DEV_DEPENDS
    
    # load the existing version
    setup_cfg = ConfigParser.ConfigParser()
    setup_cfg.read(setup_file)

    if not(setup_cfg.has_option(DEV_SECTION, DEV_DEPENDS)):
        return []
    else:
        return [n.strip() for n in
                setup_cfg.get(DEV_SECTION, DEV_DEPENDS).strip().split()]

def check_dirs(*dirs):
    """Check that our target directories all exist."""

    for d in dirs:
        if not(os.path.exists(os.path.abspath(d))):
            os.makedirs(os.path.abspath(d))

def cmdline_parser():
    """Create an option parser and populate our available options."""

    parser = optparse.OptionParser()
    parser.add_option("-s", "--file", dest="setup_cfg",
                      help="File to read setup configuration from." )
    parser.add_option("-l", "--libdir", dest="libdir",
                      help="Location of Python libraries.")
    parser.add_option("-b", "--bindir", dest="bindir",
                      help="Location of Python scripts.")
    parser.add_option("-f", "--find-dirs", dest="finddirs",
                      help="Location to examine for package links.")

    parser.set_defaults(setup_cfg="setup.cfg",
                        libdir=None,
                        bindir=None,
                        finddirs="http://download.zope.org/distribution/")

    return parser

def main():
    (options, args) = cmdline_parser().parse_args()

    # update setup.cfg with the lib dir, bin dir, etc
    updateSetupCfg(options.setup_cfg, options)
    
    # make sure that the lib directory structure of our prefix exists
    check_dirs(options.bindir, options.libdir)
    sys.path.insert(0, options.libdir)

    # bootstrap setuptools into our libdir
    bootstrap(options.libdir, options.bindir)

    # install the development dependencies
    from setuptools.command.easy_install import main as einstall
    deps = load_dev_deps(options.setup_cfg)
    if deps and len(deps) > 0:
        einstall(deps)
    
if __name__ == '__main__':
    main()
