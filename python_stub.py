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


def install_pip_and_modules(package_names):
    import os
    import os.path
    import sys
    import shutil
    import subprocess

    assert sys.version_info >= (2, 7) or sys.version_info >= (3, 4), 'Python 2.7+ or 3.4+ required'

    count_installed_packages = 0

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

    def determine_install_as_user():
        in_virtualenv = 'VIRTUAL_ENV' in os.environ
        is_root = hasattr(os, 'geteuid') and os.geteuid() == 0

        return not in_virtualenv and not is_root

    def restart():
        print('Restarting')

        os.system(sys.executable + ' ' + str(' '.join(sys.argv)))
        exit(0)

    def get_installed_packages():
        packages = {}

        output_lines = subprocess.check_output([
            sys.executable,
            '-m',
            'pip',
            'list'
        ]).decode('utf-8').split('\n')

        for iline in output_lines[2:]:
            iline = iline.strip()
            if not iline:
                continue

            parts = iline.split(' ')
            packages[parts[0]] = parts[len(parts) - 1]

        return packages

    install_as_user = determine_install_as_user()

    # install pip
    try:
        import pip
    except ImportError as x1:
        print(x1)

        download_file('https://bootstrap.pypa.io/get-pip.py')

        print('Installing: pip')

        cmd = sys.executable + ' get-pip.py'

        if install_as_user:
            cmd += ' --user'

        print('Executing: ' + cmd)

        os.system(cmd)
        os.remove('get-pip.py')

        count_installed_packages += 1

        try:
            import pip
        except ImportError:
            print('Unable to install pip')
            exit(1)

    installed_packages = get_installed_packages()
    cwd = os.getcwd()

    # check if we need Dulwich - pure Python Git implementation
    need_dulwich = False
    for ipackage_name2 in package_names:
        if ipackage_name2.startswith('git+https://'):
            need_dulwich = True
            break

    if need_dulwich:
        if not 'dulwich' in installed_packages:
            pip_install_module('dulwich', install_as_user)
            count_installed_packages += 1

            installed_packages = get_installed_packages()

            if not 'dulwich' in installed_packages:
                print('Unable to install dulwich')
                exit(1)

            restart()

    # install packages
    for ipackage_name in package_names:
        imodule_pip_basename = os.path.basename(ipackage_name)

        if not imodule_pip_basename in installed_packages:
            print('Installing: {} ({})'.format(ipackage_name, ipackage_name))

            if ipackage_name.startswith('git+https://'):
                import dulwich.porcelain

                # just remove git+ and install
                pkg_url = ipackage_name[4:]
                pkg_basename = os.path.basename(pkg_url)

                try:
                    shutil.rmtree(os.path.join(cwd, pkg_basename))
                except OSError:
                    pass

                dulwich.porcelain.clone(pkg_url)
                pip_install_module(pkg_basename, install_as_user)
                count_installed_packages += 1

                try:
                    shutil.rmtree(os.path.join(cwd, pkg_basename))
                except Exception as x5:
                    print(x5)
            else:
                pip_install_module(ipackage_name, install_as_user)
                count_installed_packages += 1

    installed_packages = get_installed_packages()

    for ipackage_name2 in package_names:
        imodule_pip_name2 = os.path.basename(ipackage_name2)

        if imodule_pip_name2 not in installed_packages:
            print('Unable to install ' + imodule_pip_name2)
            exit(1)

    if count_installed_packages > 0:
        restart()


# this will install some packages
install_pip_and_modules([
    'selenium',
    'git+https://github.com/boppreh/mouse'
])

# packages installed
# rest of your code goes below
# this lines


import selenium
import mouse


def main():
    pass

if __name__ == '__main__':
    main()
