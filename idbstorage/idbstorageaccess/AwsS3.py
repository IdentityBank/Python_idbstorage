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

import boto3


################################################################################
# Module                                                                       #
################################################################################


class AwsS3:
    configuration = None
    region_name = None
    aws_access_key_id = None
    aws_secret_access_key = None
    bucket_name = None
    s3Client = None

    def __init__(self, configuration):
        try:
            self.configuration = configuration
            self.region_name = self.configuration['region_name']
            self.aws_access_key_id = self.configuration['aws_access_key_id']
            self.aws_secret_access_key = self.configuration['aws_secret_access_key']
            self.bucket_name = self.configuration['bucket_name']
        except:
            errorMessage = 'There is not all the required data to connect to the AWS S3 bucket.'
            logging.error(errorMessage)
            raise ValueError(errorMessage)

    def initClient(self):
        try:
            if self.s3Client is None:
                self.s3Client = boto3.client('s3',
                                             region_name=self.region_name,
                                             aws_access_key_id=self.aws_access_key_id,
                                             aws_secret_access_key=self.aws_secret_access_key)
        except Exception as e:
            logging.error('AWS S3 - init client')
            logging.error(e)

    def deleteObject(self, objectKey):

        returnValue = False
        try:
            if self.s3Client is None:
                self.initClient()

            response = self.s3Client.delete_object(
                Bucket=self.bucket_name,
                Key=objectKey
            )

            if 'DeleteMarker' in response:
                returnValue = response['DeleteMarker']

        except Exception as e:
            logging.error('AWS S3 - delete object')
            logging.error(e)

        return returnValue

    def getObjects(self, maxKeys=25, encodingType='url', delimiter='/'):

        returnValue = {}
        try:
            if self.s3Client is None:
                self.initClient()

            response = self.s3Client.list_objects_v2(
                Bucket=self.bucket_name,
                Delimiter=delimiter,
                EncodingType=encodingType,
                MaxKeys=maxKeys,
                Prefix=self.configuration['s3_prefix']
            )

            if 'Contents' in response:
                returnValue['Contents'] = response['Contents']
            if 'CommonPrefixes' in response:
                returnValue['CommonPrefixes'] = response['CommonPrefixes']

        except Exception as e:
            logging.error('AWS S3 - get objects')
            logging.error(e)

        return returnValue

    def initObjectUpload(self, objectData, expiration=300):

        returnValue = {}
        try:
            logging.debug('Init Object Post Command: [{}]'.format(objectData))

            if self.s3Client is None:
                self.initClient()

            from botocore.exceptions import ClientError
            try:
                if 'upload_expiration' in self.configuration:
                    expiration = self.configuration['upload_expiration']

                response = self.s3Client.generate_presigned_post(self.configuration['bucket_name'],
                                                                 objectData['s3_key'],
                                                                 Fields=None,
                                                                 Conditions=None,
                                                                 ExpiresIn=expiration)
                if response and \
                        isinstance(response, dict) and \
                        'url' in response and \
                        'fields' in response:
                    logging.debug('Init Object Upload - AWS response: [{}]'.format(response))
                    returnValue['formAttributes'] = \
                        {
                            'action': response['url'],
                            'method': 'POST',
                            'enctype': 'multipart/form-data'
                        }
                    returnValue['formInputs'] = response['fields']
                    returnValue = json.dumps(returnValue)
                logging.debug('Init Object Upload - Post data: [{}]'.format(returnValue))

            except ClientError as e:
                returnValue = {}
                logging.error('AWS S3 - upload object - ClientError')
                logging.error(e)

        except Exception as e:
            returnValue = {}
            logging.error('AWS S3 - upload object')
            logging.error(e)

        return returnValue

    def initObjectDownload(self, objectData, expiration=300):
        returnValue = {}
        try:
            logging.debug('Init Object Download Command: [{}]'.format(objectData))

            if self.s3Client is None:
                self.initClient()

            from botocore.exceptions import ClientError
            try:
                if 'download_expiration' in self.configuration:
                    expiration = self.configuration['download_expiration']

                params = {'Bucket': self.configuration['bucket_name'],
                          'Key': objectData['s3_key']}
                if 'filename' in objectData:
                    params['ResponseContentDisposition'] = "attachment;filename={}".format(objectData['filename'])
                response = self.s3Client.generate_presigned_url('get_object', Params=params, ExpiresIn=expiration)
                if response:
                    returnValue['downloadUrl'] = response
            except ClientError as e:
                returnValue = {}
                logging.error('AWS S3 - download object - ClientError')
                logging.error(e)

        except Exception as e:
            returnValue = {}
            logging.error('AWS S3 - download object')
            logging.error(e)

        return returnValue

    def getObjectInfo(self, objectData):
        returnValue = {}
        try:
            logging.debug('Get Object Info: [{}]'.format(objectData))

            if self.s3Client is None:
                self.initClient()

            params = {'Bucket': self.configuration['bucket_name'],
                      'Key': objectData['s3_key']}
            response = self.s3Client.get_object(**params)
            if response and 'ResponseMetadata' in response:
                returnValue['info'] = response['ResponseMetadata']

        except Exception as e:
            returnValue = {}
            logging.error('AWS S3 - download object')
            logging.error(e)

        return returnValue

    @staticmethod
    def idb(configuration):
        return AwsS3(configuration)

################################################################################
#                                End of file                                   #
################################################################################
