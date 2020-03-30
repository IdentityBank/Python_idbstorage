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

import json
import logging
import socket

from secureclientserverservice import ScssClientInet
from secureclientserverservice import ScssProtocol
from secureclientserverservice import ScssSecurityHelper


################################################################################
# Module                                                                       #
################################################################################

class IdbClientInet(ScssClientInet):

    @staticmethod
    def connect(host, port, connectionType=socket.SOCK_STREAM):
        scssClient = IdbClientInet(host, port, connectionType)
        if scssClient._connect():
            return scssClient
        else:
            return None

    @staticmethod
    def connectWithConfig(config):
        logging.info('Client config ...')
        logging.info(json.dumps(config, indent=4))
        scssClient = IdbClientInet.connect(config['host'], config['port'])
        if scssClient:
            scssClient.setConfiguration(config)
            scssClient.setConnectionSecurity(ScssSecurityHelper.load(config))
        return scssClient

    def sendNone(self, data):
        receivedString = None
        try:
            logging.debug("Send [None] data.")
            ScssProtocol.sendNoneData(self.clientSocket, data)
            logging.debug("Data sent.")
            receivedString = ScssProtocol.receiveNoneData(self.clientSocket, self.max_buffer_size)
            logging.debug("Data received.")
            logging.debug("Data [{}]".format(receivedString))
        except socket.timeout:
            logging.debug("Connection timeout.")

        return receivedString

    def sendToken(self, data):
        logging.warning('TOKEN access not implemented yet!')
        return None

    def sendCertificate(self, data):
        logging.warning('CERTIFICATE access not implemented yet!')
        return None

    @staticmethod
    def actionCostData(dataJson):
        actionCost = None
        try:
            if dataJson and isinstance(dataJson, str):
                data = json.loads(dataJson)
                if 'result' in data:
                    data = json.loads(data['result'])
                    if 'CountAll' in data and \
                            'QueryData' in data:
                        actionCost = {}
                        for item in data['QueryData']:
                            if 4 <= len(item):
                                actionCost[item[2]] = item[1]
        except:
            actionCost = None
        return actionCost

################################################################################
#                                End of file                                   #
################################################################################
