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

import logging
import re
import uuid


################################################################################
# Module                                                                       #
################################################################################

class IdbStorageObject:
    __version = 1
    __template = "{storage_id}.{year}{month}{day}{hour}{minute}{second}{microsecond}.{requester_uuid}.{object_uuid}"

    @staticmethod
    def generateObjectId(configuration: dict,
                         attributes: dict) -> str:

        returnValue = None
        try:
            if isinstance(configuration, dict) and \
                    'storage_id' in configuration and \
                    isinstance(attributes, dict) and \
                    'requester' in attributes:
                attributes['storage_id'] = configuration['storage_id']
                attributes['requester_uuid'] = uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    "{year}{microsecond}{month}{minute}{day}".format(**attributes) +
                    attributes['requester']
                )
                attributes['object_uuid'] = uuid.uuid4()
                returnValue = IdbStorageObject.__template.format(**attributes)
                logging.debug(returnValue)

        except Exception as e:
            logging.error('IDB Storage - generate object ID')
            logging.error(str(e))

        return returnValue

    @staticmethod
    def __parseObjectId(objectId: str) -> dict:
        objectIdDict = None
        objectIdKeys = ['storage_id', 'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond',
                        'requester_uuid', 'object_uuid']
        objectIdRegex = "([\w]+).(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{6}).([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}).([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})"
        objectIdRegexMatch = re.match(objectIdRegex, objectId)
        if objectIdRegexMatch:
            objectIdRegexGroups = objectIdRegexMatch.groups()
            if objectIdRegexGroups and len(objectIdRegexMatch.groups()) == 10:
                objectIdDict = dict(zip(objectIdKeys, objectIdRegexGroups))
                logging.warning(objectIdDict)
        return objectIdDict

    @staticmethod
    def generateStorageData(objectId: str,
                            connectionStorage: dict) -> str:
        objectData = None
        objectIdData = IdbStorageObject.__parseObjectId(objectId)
        if objectIdData:
            storageId = objectId
            storageType = connectionStorage['type']
            if storageType.upper() == 'AWS_S3':
                if 's3_prefix' in connectionStorage:
                    objectIdData['s3_prefix'] = connectionStorage['s3_prefix']
                else:
                    objectIdData['s3_prefix'] = ''
                template_prefix_s3 = "{s3_prefix}{storage_id}/{year}/{month}/{day}/"
                storagePrefix = template_prefix_s3.format(**objectIdData)
                template_filename_s3 = "{year}{month}{day}{hour}{minute}{second}{microsecond}.{requester_uuid}.{object_uuid}"
                storageFilename = template_filename_s3.format(**objectIdData)
                template_s3 = "{s3_prefix}{storage_id}/{year}/{month}/{day}/{year}{month}{day}{hour}{minute}{second}{microsecond}.{requester_uuid}.{object_uuid}"
                storageId = template_s3.format(**objectIdData)
                objectData = {'s3_key': storageId, 's3_prefix': storagePrefix, 's3_filename': storageFilename}
        return objectData

################################################################################
#                                End of file                                   #
################################################################################
