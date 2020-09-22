#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from distutils.core import setup
import codecs
import os
from os.path import exists, isdir, join
import platform
import re
import shutil
import sys
from tempfile import gettempdir
import semantic_version

from config import appname as APPNAME, applongname as APPLONGNAME, appcmdname as APPCMDNAME, appversion as VERSION, copyright as COPYRIGHT
from config import update_feed, update_interval


if sys.platform=='win32':
    assert platform.architecture()[0]=='32bit', 'Assumes a Python built for 32bit'
    import py2exe
    dist_dir = 'dist.win32'
elif sys.platform=='darwin':
    dist_dir = 'dist.macosx'
else:
    assert False, 'Unsupported platform %s' % sys.platform

# Split version, as py2exe wants the 'base' for version
semver = semantic_version.Version.coerce(VERSION)
BASEVERSION = str(semver.truncate('patch'))

if dist_dir and len(dist_dir)>1 and isdir(dist_dir):
    shutil.rmtree(dist_dir)

# "Developer ID Application" name for signing
macdeveloperid = None

# Windows paths
WIXPATH = r'C:\Program Files (x86)\WiX Toolset v3.11\bin'
SDKPATH = r'C:\Program Files (x86)\Windows Kits\10\bin\10.0.18362.0\x86'

# OSX paths
SPARKLE = '/Library/Frameworks/Sparkle.framework'

# Patch py2app recipe enumerator to skip the sip recipe since it's too enthusiastic - we'll list additional Qt modules explicitly
if sys.platform=='darwin':
    from py2app import recipes
    import py2app.build_app
    def iterRecipes(module=recipes):
        for name in dir(module):
            if name.startswith('_') or name=='sip':
                continue
            check = getattr(getattr(module, name), 'check', None)
            if check is not None:
                yield (name, check)
    py2app.build_app.iterRecipes = iterRecipes


APP = 'EDMarketConnector.py'
APPCMD = 'EDMC.py'
SHORTVERSION = ''.join(VERSION.split('.')[:3])
PLUGINS = [ 'plugins/coriolis.py', 'plugins/eddb.py', 'plugins/eddn.py', 'plugins/edsm.py', 'plugins/edsy.py', 'plugins/inara.py' ]

if sys.platform=='darwin':
    OPTIONS =  { 'py2app':
                 {'dist_dir': dist_dir,
                  'optimize': 2,
                  'packages': [
                      'requests',
                      'sqlite3',	# Included for plugins
                  ],
                  'includes': [
                      'shutil',         # Included for plugins
                      'zipfile',        # Included for plugins
                  ],
                  'frameworks': [ 'Sparkle.framework' ],
                  'excludes': [ 'distutils', '_markerlib', 'PIL', 'pkg_resources', 'simplejson', 'unittest' ],
                  'iconfile': '%s.icns' % APPNAME,
                  'include_plugins': [('plugins', x) for x in PLUGINS],
                  'resources': [ 'commodity.csv', 'rare_commodity.csv', 'snd_good.wav', 'snd_bad.wav', 'modules.p', 'ships.p', 'stations.p', 'systems.p'],
                  'site_packages': False,
                  'plist': {
                      'CFBundleName': APPLONGNAME,
                      'CFBundleIdentifier': 'uk.org.marginal.%s' % APPNAME.lower(),
                      'CFBundleLocalizations': sorted(set([x[:-len('.lproj')] for x in os.listdir(join(SPARKLE, 'Resources')) if x.endswith('.lproj')]) | set([x[:-len('.strings')] for x in os.listdir('L10n') if x.endswith('.strings')])),	# https://github.com/sparkle-project/Sparkle/issues/238
                      'CFBundleShortVersionString': VERSION,
                      'CFBundleVersion':  VERSION,
                      'CFBundleURLTypes': [
                          {
                              'CFBundleTypeRole': 'Viewer',
                              'CFBundleURLName': 'uk.org.marginal.%s.URLScheme' % APPNAME.lower(),
                              'CFBundleURLSchemes': ['edmc'],
                          }
                      ],
                      'LSMinimumSystemVersion': '10.10',
                      'NSAppleScriptEnabled': True,
                      'NSHumanReadableCopyright': COPYRIGHT,
                      'SUEnableAutomaticChecks': True,
                      'SUShowReleaseNotes': True,
                      'SUAllowsAutomaticUpdates': False,
                      'SUFeedURL': update_feed,
                      'SUScheduledCheckInterval': update_interval,
                  },
                  'graph': True,	# output dependency graph in dist
              }
    }
    DATA_FILES = []

elif sys.platform=='win32':
    OPTIONS =  { 'py2exe':
                 {'dist_dir': dist_dir,
                  'optimize': 2,
                  'packages': [
                      'requests',
                      'sqlite3',	# Included for plugins
                  ],
                  'includes': [
                      'dataclasses',
                      'shutil',         # Included for plugins
                      'timeout_session',
                      'zipfile',        # Included for plugins
                  ],
                  'excludes': [ 'distutils', '_markerlib', 'optparse', 'PIL', 'pkg_resources', 'simplejson', 'unittest' ],
              }
    }

    DATA_FILES = [
        ('', [
            'WinSparkle.dll',
            'WinSparkle.pdb',	# For debugging - don't include in package
            'EUROCAPS.TTF',
            'Changelog.md',
            'commodity.csv',
            'rare_commodity.csv',
            'snd_good.wav',
            'snd_bad.wav',
            'modules.p',
            'ships.p',
            'stations.p',
            'systems.p',
            '%s.VisualElementsManifest.xml' % APPNAME,
            '%s.ico' % APPNAME,
            '%s/DLLs/sqlite3.dll' % (sys.base_prefix),
        ]),
        ('L10n', [join('L10n',x) for x in os.listdir('L10n') if x.endswith('.strings')]),
        ('plugins', PLUGINS),
    ]

setup(
    name = APPLONGNAME,
    version = VERSION,
    windows = [ {'dest_base': APPNAME,
                 'script': APP,
                 'icon_resources': [(0, '%s.ico' % APPNAME)],
                 'company_name': 'EDCD',  # WinSparkle
                 'product_name': APPNAME,  # WinSparkle
                 'version': BASEVERSION,
                 'product_version': VERSION,
                 'copyright': COPYRIGHT,
                 'other_resources': [(24, 1, open(APPNAME+'.manifest').read())],
             } ],
    console = [ {'dest_base': APPCMDNAME,
                 'script': APPCMD,
                 'company_name': 'EDCD',
                 'product_name': APPNAME,
                 'version': BASEVERSION,
                 'product_version': VERSION,
                 'copyright': COPYRIGHT,
                 'other_resources': [(24, 1, open(APPCMDNAME+'.manifest').read())],
             } ],
    data_files = DATA_FILES,
    options = OPTIONS,
)

PKG = None
if sys.platform == 'darwin':
    if isdir('%s/%s.app' % (dist_dir, APPLONGNAME)):	# from CFBundleName
        os.rename('%s/%s.app' % (dist_dir, APPLONGNAME), '%s/%s.app' % (dist_dir, APPNAME))

        # Generate OSX-style localization files
        for x in os.listdir('L10n'):
            if x.endswith('.strings'):
                lang = x[:-len('.strings')]
                path = '%s/%s.app/Contents/Resources/%s.lproj' % (dist_dir, APPNAME, lang)
                os.mkdir(path)
                codecs.open('%s/Localizable.strings' % path, 'w', 'utf-16').write(codecs.open('L10n/%s' % x, 'r', 'utf-8').read())

        if macdeveloperid:
            os.system('codesign --deep -v -s "Developer ID Application: %s" %s/%s.app' % (macdeveloperid, dist_dir, APPNAME))
        # Make zip for distribution, preserving signature
        PKG = '%s_mac_%s.zip' % (APPNAME, VERSION)
        os.system('cd %s; ditto -ck --keepParent --sequesterRsrc %s.app ../%s; cd ..' % (dist_dir, APPNAME, PKG))
elif sys.platform == 'win32':
    os.system(r'"%s\candle.exe" -out %s\ %s.wxs' % (WIXPATH, dist_dir, APPNAME))
    if not exists('%s/%s.wixobj' % (dist_dir, APPNAME)):
        raise AssertionError('No %s/%s.wixobj: candle.exe failed?' % (dist_dir, APPNAME))

    PKG = '%s_win_%s.msi' % (APPNAME, VERSION)
    import subprocess
    os.system(r'"%s\light.exe" -sacl -spdb -sw1076 %s\%s.wixobj -out %s' % (WIXPATH, dist_dir, APPNAME, PKG))
    if not exists(PKG):
        raise AssertionError('light.exe failed, no %s' % (PKG))

    # Seriously, this is how you make Windows Installer use the user's display language for its dialogs. What a crock.
    # http://www.geektieguy.com/2010/03/13/create-a-multi-lingual-multi-language-msi-using-wix-and-custom-build-scripts
    lcids = [int(x) for x in re.search(r'Languages\s*=\s*"(.+?)"', open('%s.wxs' % APPNAME).read()).group(1).split(',')]
    assert lcids[0]==1033, 'Default language is %d, should be 1033 (en_US)' % lcids[0]
    shutil.copyfile(PKG, join(gettempdir(), '%s_1033.msi' % APPNAME))
    for lcid in lcids[1:]:
        shutil.copyfile(join(gettempdir(), '%s_1033.msi' % APPNAME), join(gettempdir(), '%s_%d.msi' % (APPNAME, lcid)))
        os.system(r'cscript /nologo "%s\WiLangId.vbs" %s\%s_%d.msi Product %d' % (SDKPATH, gettempdir(), APPNAME, lcid, lcid))	# Don't care about codepage because the displayed strings come from msiexec not our msi
        os.system(r'"%s\MsiTran.Exe" -g %s\%s_1033.msi %s\%s_%d.msi %s\%d.mst' % (SDKPATH, gettempdir(), APPNAME, gettempdir(), APPNAME, lcid, gettempdir(), lcid))
        os.system(r'cscript /nologo "%s\WiSubStg.vbs" %s %s\%d.mst %d' % (SDKPATH, PKG, gettempdir(), lcid, lcid))
else:
    raise AssertionError('Unsupported platform')

if not exists(PKG):
    raise AssertionError('No %s found prior to appcast' % (PKG))
# Make appcast entry
appcast = open('appcast_%s_%s.xml' % (sys.platform=='darwin' and 'mac' or 'win', VERSION), 'w')
appcast.write('''
\t\t<item>
\t\t\t<title>Release {VERSION}</title>
\t\t\t<description>
\t\t\t\t<![CDATA[
<style>{STYLE}</style>
<h2>Release {VERSION}</h2>
<ul>

</ul>
\t\t\t\t]]>
\t\t\t</description>
\t\t\t<enclosure
\t\t\t\turl="https://github.com/EDCD/EDMarketConnector/releases/download/rel-{VERSION}/{PKG}"
\t\t\t\tsparkle:os="{OS}"
\t\t\t\tsparkle:version="{VERSION}"
\t\t\t\tlength="{LENGTH}"
\t\t\t\ttype="application/octet-stream"
\t\t\t/>
\t\t</item>
'''.format(VERSION=VERSION,
           STYLE='{}'.format(
                sys.platform=='win32' and 'body { font-family:"Segoe UI","Tahoma"; font-size: 75%; } h2 { font-family:"Segoe UI","Tahoma"; font-size: 105%; }' 
                or 'h2 { font-size: 105%; }'),
           PKG=PKG,
           OS=''.format(sys.platform=='win32' and 'windows"\n\t\t\t\tsparkle:installerArguments="/passive LAUNCH=yes' or 'macos'),
           LENGTH=os.stat(PKG).st_size)
)
