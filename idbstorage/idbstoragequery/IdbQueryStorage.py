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

from psycopg2 import sql

from idbstorage import IdbCommon, AwsS3
from .IdbQueryError import IdbQueryError
from .IdbQueryResponse import IdbQueryResponse
from .IdbQuerySql import IdbQuerySql
from .IdbSqlQueryBuilder import IdbSqlQueryBuilder


################################################################################
# Module                                                                       #
################################################################################

class IdbQueryStorage:

    @staticmethod
    def executeQuery(configuration: dict,
                     queryData: dict) -> str:

        returnValue = IdbQueryError.requestError()

        try:
            if isinstance(queryData, dict) and 'query' in queryData and configuration['connectionDatabase']:

                queryData['dbTableSchema'] = 'idbstorage'
                queryData['dbTableSchemaIdentifier'] = sql.Identifier(queryData['dbTableSchema'])
                queryData['dbTableName'] = "{businessDbId}"
                if 'dbHost' in configuration['connectionDatabase'] and \
                        'dbPort' in configuration['connectionDatabase'] and \
                        'dbName' in configuration['connectionDatabase'] and \
                        'dbUser' in configuration['connectionDatabase'] and \
                        'dbPassword' in configuration['connectionDatabase']:
                    dbConnection = {
                        "host": configuration['connectionDatabase']['dbHost'],
                        "port": configuration['connectionDatabase']['dbPort'],
                        "database": configuration['connectionDatabase']['dbName'],
                        "user": configuration['connectionDatabase']['dbUser'],
                        "password": configuration['connectionDatabase']['dbPassword'],
                    }
                    if logging.getLevelName(logging.getLogger().getEffectiveLevel()) == 'DEBUG':
                        dbConnectionPrint = dbConnection.copy()
                        dbConnectionPrint.pop("password")
                        logging.debug(json.dumps(dbConnectionPrint))

                ################################################################################
                # IDB Storage Object                                                           #
                ################################################################################

                if queryData['query'] == 'initObject':
                    attributes = IdbCommon.getTimestempDict(time=True,
                                                            seconds=True,
                                                            microseconds=True,
                                                            utc=True)
                    from idbstorage import IdbStorageObject
                    queryData['objectId'] = IdbStorageObject.generateObjectId(configuration['connectionStorage'],
                                                                              {**attributes, **queryData})
                    if queryData['objectId']:
                        queryData['storageData'] = IdbStorageObject.generateStorageData(queryData['objectId'],
                                                                                        configuration[
                                                                                            'connectionStorage'])
                        s3Bucket = AwsS3.idb(configuration['connectionStorage'])
                        awsS3Post = s3Bucket.initObjectUpload(queryData['storageData'])
                        queryData['data'] = {'oid': queryData['objectId'],
                                             'storage': json.dumps(
                                                 queryData['storageData'])
                                             if queryData['storageData']
                                             else None}
                        import copy
                        returnValueInsert = IdbQuerySql.fetchSqlQuery(dbConnection,
                                                                      IdbSqlQueryBuilder.generateSqlCreateObject(
                                                                          copy.deepcopy(queryData)),
                                                                      commit=True,
                                                                      returnDataOnly=True)
                        if 'Query' in returnValueInsert and returnValueInsert['Query'] == 1 and \
                                'QueryData' in returnValueInsert and returnValueInsert['QueryData'][0][0] == queryData[
                            'objectId']:
                            returnValue = IdbQuerySql.fetchSqlQuery(dbConnection,
                                                                    IdbSqlQueryBuilder.generateSqlGetObject(
                                                                        queryData),
                                                                    returnDataOnly=True)

                            if 'Query' in returnValue:
                                returnValue['AwsS3Post'] = awsS3Post
                                returnValue = IdbQueryResponse.responseOkDict(returnValue)

                elif queryData['query'] == 'editStorageObject':
                    queryData['account'] = "idbobjects"
                    if 'data' in queryData:
                        allowedUpdateKeys = ['tag', 'metadata', 'attributes']
                        data = queryData['data']
                        queryData['data'] = {}
                        for key in allowedUpdateKeys:
                            if key in data:
                                if isinstance(data[key], str):
                                    queryData['data'][key] = data[key]
                                else:
                                    queryData['data'][key] = json.dumps(data[key])
                        queryData['data']['updatetime'] = 'NOW()'
                    returnValue = IdbQuerySql.executeSqlQuery(dbConnection,
                                                              IdbSqlQueryBuilder.generateSqlEditObject(
                                                                  queryData))

                elif queryData['query'] == 'deleteStorageObject':
                    s3Bucket = AwsS3.idb(configuration['connectionStorage'])
                    if s3Bucket.deleteObject():
                        queryData['account'] = "idbobjects"
                        returnValue = IdbQuerySql.executeSqlQuery(dbConnection,
                                                                  IdbSqlQueryBuilder.generateSqlDeleteObject(
                                                                      queryData))
                    else:
                        returnValue = IdbQueryError.requestInternalServerError()

                elif queryData['query'] == 'findCountAllStorageObjects':
                    queryData['account'] = "idbobjects"
                    returnValue = IdbQueryStorage.__findCountAllTable(queryData, dbConnection)

                elif queryData['query'] == 'downloadStorageObject':
                    queryData['account'] = "idbobjects"
                    queryData['DataTypes'] = \
                        {
                            "database": ["id", "oid", "storage", "metadata"]
                        }
                    returnValue = IdbQuerySql.fetchSqlQuery(dbConnection,
                                                            IdbSqlQueryBuilder.generateSqlGetObject(
                                                                queryData), returnDataOnly=True)

                    if returnValue and 'QueryData' in returnValue and returnValue['QueryData']:
                        objectId = returnValue['QueryData'][0][1]

                        try:
                            storageData = json.loads(returnValue['QueryData'][0][2])
                        except json.JSONDecodeError as e:
                            storageData = {}
                            logging.error(e)
                        except Exception as e:
                            storageData = {}
                            logging.error(e)

                        try:
                            metadataData = json.loads(returnValue['QueryData'][0][3])
                        except json.JSONDecodeError as e:
                            metadataData = {}
                            logging.error(e)
                        except Exception as e:
                            metadataData = {}
                            logging.error(e)

                        if 'filename' in queryData:
                            storageData['filename'] = queryData['filename']

                        s3Bucket = AwsS3.idb(configuration['connectionStorage'])
                        awsS3Get = s3Bucket.initObjectDownload({**metadataData, **storageData})
                        if 'downloadUrl' in awsS3Get:
                            returnValue = IdbQueryResponse.responseOkDict({**{"oid": objectId}, **awsS3Get})
                        else:
                            returnValue = IdbQueryError.requestNotFound()
                    else:
                        returnValue = IdbQueryError.requestNotFound()

                elif queryData['query'] == 'infoStorageObject':
                    queryData['account'] = "idbobjects"
                    queryData['DataTypes'] = \
                        {
                            "database": ["id", "oid", "storage"]
                        }
                    returnValue = IdbQuerySql.fetchSqlQuery(dbConnection,
                                                            IdbSqlQueryBuilder.generateSqlGetObject(
                                                                queryData), returnDataOnly=True)

                    if returnValue and 'QueryData' in returnValue and returnValue['QueryData']:
                        objectId = returnValue['QueryData'][0][1]

                        try:
                            storageData = json.loads(returnValue['QueryData'][0][2])
                        except json.JSONDecodeError as e:
                            storageData = {}
                            logging.error(e)
                        except Exception as e:
                            storageData = {}
                            logging.error(e)

                        s3Bucket = AwsS3.idb(configuration['connectionStorage'])
                        awsS3ObjectInfo = s3Bucket.getObjectInfo(storageData)
                        if 'info' in awsS3ObjectInfo:
                            returnValue = IdbQueryResponse.responseOkDict({**{"oid": objectId}, **awsS3ObjectInfo})
                        else:
                            returnValue = IdbQueryError.requestNotFound()
                    else:
                        returnValue = IdbQueryError.requestNotFound()

                ################################################################################
                # IDB Storage Item                                                             #
                ################################################################################

                elif queryData['query'] == 'addStorageItem':
                    queryData['account'] = "idbitems"
                    returnValue = IdbQuerySql.fetchSqlQuery(dbConnection,
                                                            IdbSqlQueryBuilder.generateSqlAddStorageItem(
                                                                queryData), True)

                elif queryData['query'] == 'editStorageItem':
                    queryData['account'] = "idbitems"
                    if 'id' in queryData:
                        del queryData['id']
                    if 'itemId' in queryData:
                        queryData['id'] = queryData['itemId']
                    if 'data' in queryData:
                        allowedUpdateKeys = ['pid', 'name', 'metadata', 'permission']
                        data = queryData['data']
                        queryData['data'] = {}
                        for key in allowedUpdateKeys:
                            if key in data:
                                if isinstance(data[key], str):
                                    queryData['data'][key] = data[key]
                                else:
                                    queryData['data'][key] = json.dumps(data[key])
                        queryData['data']['updatetime'] = 'NOW()'
                    returnValue = IdbQuerySql.executeSqlQuery(dbConnection,
                                                              IdbSqlQueryBuilder.generateSqlEditItem(
                                                                  queryData))

                elif queryData['query'] == 'deleteStorageItem':
                    queryData['account'] = "idbitems"
                    if 'id' in queryData:
                        del queryData['id']
                    if 'itemId' in queryData:
                        queryData['id'] = queryData['itemId']
                    returnValue = IdbQuerySql.executeSqlQuery(dbConnection,
                                                              IdbSqlQueryBuilder.generateSqlDeleteItem(
                                                                  queryData))

                elif queryData['query'] == 'deleteStorageItemsByObjectId':
                    queryData['account'] = "idbitems"
                    if 'oid' in queryData:
                        del queryData['oid']
                    if 'objectId' in queryData:
                        queryData['oid'] = queryData['objectId']
                    returnValue = IdbQuerySql.executeSqlQuery(dbConnection,
                                                              IdbSqlQueryBuilder.generateSqlDeleteItemsByObjectId(
                                                                  queryData))

                elif queryData['query'] == 'findCountAllStorageItems':
                    queryData['account'] = "idbitems"
                    returnValue = IdbQueryStorage.__findCountAllTable(queryData, dbConnection)

                else:
                    returnValue = IdbQueryError.requestNotImplemented()

        except Exception as e:
            returnValue = IdbQueryError.requestUnsupportedService(str(e))
            logging.error('Query error')
            logging.error(e)

        return returnValue

    @staticmethod
    def __findCountAllTable(queryData, dbConnection) -> str:
        if 'dbTableLimit' not in queryData:
            queryData['dbTableLimit'] = 0
        returnValue = IdbQuerySql.fetchSqlQuery(dbConnection,
                                                IdbSqlQueryBuilder.generateSqlCountTable(
                                                    dict(queryData)), False, True)
        if returnValue \
                and isinstance(returnValue, dict) \
                and 'Query' in returnValue \
                and returnValue['Query'] == 1 \
                and 'QueryData' in returnValue:
            countAll = returnValue['QueryData']
            if 'dbTableLimit' not in queryData:
                queryData['dbTableLimit'] = 0
            returnValue = IdbQuerySql.fetchSqlQuery(dbConnection,
                                                    IdbSqlQueryBuilder.generateSqlFindTable(
                                                        queryData), False, True)
            if returnValue \
                    and isinstance(returnValue, dict) \
                    and 'Query' in returnValue \
                    and 'QueryData' in returnValue:
                returnValue['CountAll'] = countAll
                returnValue = IdbQueryResponse.responseOkDict(returnValue)
            else:
                returnValue = IdbQueryError.requestQueryError()
        else:
            returnValue = IdbQueryError.requestQueryError()
        return returnValue

################################################################################
#                                End of file                                   #
################################################################################
