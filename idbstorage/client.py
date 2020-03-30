#! /bin/sh
# -*- coding: utf-8 -*-
""":"
exec python3 $0 ${1+"$@"}
"""
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

import argparse
import logging
import re
import signal
import sys

from idbstorage import ProcessQuery

################################################################################
# Module Variable(s)                                                           #
################################################################################

versionString = "0.0.1"
applicationNameString = "idbstorageclient"
applicationDescriptionString = "IDB Storage - tools to store and manage IDB assets"


################################################################################
# Module                                                                       #
################################################################################

def parameters():
    parser = argparse.ArgumentParser(description=applicationDescriptionString)
    parser.add_argument('-v', '--version', action='version',
                        version=applicationNameString + " - " + versionString + " - " + applicationDescriptionString)
    parser.add_argument('-i', '--jscConfigFilePath', type=argparse.FileType('r'), help='Path to config file.',
                        required=True)
    parser.add_argument('-n', '--connectionName',
                        help='Connection name.', required=True)
    parser.add_argument('-q', '--inputQueryFilePath',
                        help='The IDB query.', required=True)

    loggingLeveChoices = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }
    parser.add_argument('-ll', '--logging_level', dest="loggingLevel", choices=loggingLeveChoices.keys(),
                        help='Output log level', required=False)
    args, leftovers = parser.parse_known_args()

    if vars(args)['loggingLevel'] is None:
        level = logging.CRITICAL
    else:
        level = loggingLeveChoices.get(vars(args)['loggingLevel'], logging.CRITICAL)
    logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(module)-20s] - %(message)s',
                        datefmt='%Y.%m.%d %H:%M.%S', level=level)

    return vars(args)


def main(argv=sys.argv):
    signal.signal(signal.SIGINT, handler)
    args = parameters()
    logging.info('* Arguments:')
    for key, value in args.items():
        logging.info('** [{}]: [{}]'.format(' '.join(
            ''.join([w[0].upper(), w[1:].lower()]) for w in (re.sub("([a-z])([A-Z])", "\g<1> \g<2>", key)).split()),
            value))

    print("Loading config file: {}".format(args['jscConfigFilePath'].name))
    print("Your request is processing. Wait...")

    if args['loggingLevel'] == 'DEBUG':
        print(ProcessQuery.executeFromFile(args['jscConfigFilePath'].name, args['connectionName'],
                                           args['inputQueryFilePath']))
    else:
        try:
            print(ProcessQuery.executeFromFile(args['jscConfigFilePath'].name, args['connectionName'],
                                               args['inputQueryFilePath']))
        except:
            print('Error!')

    print("Done.")


def handler(signum, frame):
    sys.exit()


# Execute main function
if __name__ == '__main__':
    main()
    sys.exit()

################################################################################
#                                End of file                                   #
################################################################################
