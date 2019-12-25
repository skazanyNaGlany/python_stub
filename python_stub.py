#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2019 Paweł Kacperski (screamingbox@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def install_pip_and_modules(module_names):
    import os
    import sys
    import importlib
    import shutil

    try:
        import urllib2
    except ModuleNotFoundError:
        import urllib.request

    def download_file(url):
        print('Downloading ' + url)

        if 'urllib2' in globals() or 'urllib2' in locals():
            remote_file = urllib2.urlopen(url)
        elif 'urllib' in globals() or 'urllib' in locals():
            remote_file = urllib.request.urlopen(url)

        with open(os.path.basename(url), 'wb') as local_file:
            local_file.write(remote_file.read())

    def pip_install_module(module_name, as_user):
        cmd = sys.executable + ' -m pip install ' + module_name

        if as_user:
            cmd += ' --user'

        print('Executing: ' + cmd)
        os.system(cmd)

    in_virtualenv = 'VIRTUAL_ENV' in os.environ
    is_root = hasattr(os, 'geteuid') and os.geteuid() == 0
    install_as_user = not in_virtualenv and not is_root

    try:
        import pip
    except ImportError as x1:
        print(x1)

        download_file('https://bootstrap.pypa.io/get-pip.py')

        print('Installing: pip')

        if in_virtualenv:
            cmd = sys.executable + ' get-pip.py'
        else:
            cmd = sys.executable + ' get-pip.py --user'

        print('Executing: ' + cmd)

        os.system(cmd)
        os.remove('get-pip.py')

        try:
            import pip
        except ImportError:
            print('Unable to install pip')
            exit(1)

    module_names_list = module_names.keys()
    cwd = os.getcwd()

    # check if we need Dulwich - pure Python Git implementation
    need_dulwich = False
    for imodule_name2 in module_names:
        if module_names[imodule_name2].startswith('git+https://'):
            need_dulwich = True
            break

    if need_dulwich:
        try:
            import dulwich
        except ImportError as x4:
            print(x4)

            pip_install_module('dulwich', install_as_user)

    for imodule_name in module_names_list:
        try:
            globals()[imodule_name] = importlib.import_module(imodule_name)
        except ImportError as x2:
            print(x2)

            imodule_pip_name = module_names[imodule_name]

            print('Installing: {} ({})'.format(imodule_name, imodule_pip_name))

            if imodule_pip_name.startswith('git+https://'):
                import dulwich.porcelain

                # just remove git+ and install
                pkg_url = imodule_pip_name[4:]
                pkg_basename = os.path.basename(pkg_url)

                try:
                    shutil.rmtree(os.path.join(cwd, pkg_basename))
                except OSError:
                    pass

                dulwich.porcelain.clone(pkg_url)
                pip_install_module(pkg_basename, install_as_user)

                try:
                    shutil.rmtree(os.path.join(cwd, pkg_basename))
                except Exception as x5:
                    print(x5)
            else:
                pip_install_module(imodule_pip_name, install_as_user)
            try:
                globals()[imodule_name] = importlib.import_module(imodule_name)
            except ImportError as x3:
                print(x3)

                print('Unable to install module ' + imodule_name)
                exit(1)


def main():
    # this will install pip and selenium
    # and import selenium
    install_pip_and_modules({
        'selenium': 'selenium',
        'mouse': 'git+https://github.com/boppreh/mouse'
        # 'mouse': 'mouse'
    })

    # modules installed and imported
    # rest of your code goes below
    # this lines


if __name__ == '__main__':
    main()
