# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *                                                                       *
# *   Identity Bank storage system                                        *
# *   This file is part of idbstorage. This project may be found at:      *
# *   https://github.com/IdentityBank/Python_idbstorage.                  *
# *                                                                       *
# *   Copyright (C) 2020 by Identity Bank. All Rights Reserved.           *
# *   https://www.identitybank.eu - You belong to you                     *
# *                                                                       *
# *   This program is free software: you can redistribute it and/or       *
# *   modify it under the terms of the GNU Affero General Public          *
# *   License as published by the Free Software Foundation, either        *
# *   version 3 of the License, or (at your option) any later version.    *
# *                                                                       *
# *   This program is distributed in the hope that it will be useful,     *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the        *
# *   GNU Affero General Public License for more details.                 *
# *                                                                       *
# *   You should have received a copy of the GNU Affero General Public    *
# *   License along with this program. If not, see                        *
# *   https://www.gnu.org/licenses/.                                      *
# *                                                                       *
# * ********************************************************************* *

################################################################################
# Import(s)                                                                    #
################################################################################

import os

from setuptools import setup

################################################################################
# Module                                                                       #
################################################################################

description = 'IDB Storage - tools to store and manage IDB assets.'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    long_description = read('README.md')
except IOError:
    long_description = description

setup(
    name='idbstorage',
    version='0.1',
    description=description,
    long_description=long_description,
    keywords="idb storage encryption decryption share tools",
    author='Marcin Zelek',
    author_email='marcin.zelek@identitybank.eu',
    license='End-User License Agreement (EULA) of Secure Storage',
    url='We do not have URL yet',
    packages=['idbstorage',
              'idbstorage.idbstorageaccess',
              'idbstorage.idbstoragecommon',
              'idbstorage.idbstoragequery',
              'idbstorage.idbstoragehelper'],
    entry_points=
    {
        'console_scripts':
            [
                'idbstorageclient = idbstorage.client:main',
                'idbstorageserver = idbstorage.server:main',
            ],
    },
    zip_safe=False
)

################################################################################
#                                End of file                                   #
################################################################################
