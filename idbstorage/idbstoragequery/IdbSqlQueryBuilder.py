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

import idbank.idbankquery.IdbSqlQueryBuilder as IdbGenericSqlQueryBuilder
from psycopg2 import sql


################################################################################
# Module                                                                       #
################################################################################

class IdbSqlQueryBuilder:

    ################################################################################
    # IDB Storage Object                                                           #
    ################################################################################

    @staticmethod
    def generateSqlCreateObject(queryData: dict) -> str:
        queryData['dbTableColumnPk'] = "oid"
        queryData['account'] = "idbobjects"
        return IdbGenericSqlQueryBuilder.generateSqlGenericPutItem(queryData)

    @staticmethod
    def generateSqlGetObject(queryData: dict) -> str:
        queryData['dbTableColumnPk'] = "oid"
        queryData['account'] = "idbobjects"
        if 'objectId' in queryData and isinstance(queryData['objectId'], str):
            queryData['dbTablePk'] = sql.Literal(queryData['objectId'])
        return IdbGenericSqlQueryBuilder.generateSqlGenericGetItem(queryData)

    @staticmethod
    def generateSqlEditObject(queryData: dict) -> str:
        queryData['dbTableColumnPk'] = "oid"
        if 'objectId' in queryData and isinstance(queryData['objectId'], str):
            queryData['dbTablePk'] = sql.Literal(queryData['objectId'])
        return IdbGenericSqlQueryBuilder.generateSqlGenericUpdateItem(queryData)

    @staticmethod
    def generateSqlDeleteObject(queryData: dict) -> str:
        queryData['dbTableColumnPk'] = "oid"
        if 'objectId' in queryData and isinstance(queryData['objectId'], str):
            queryData['dbTablePk'] = sql.Literal(queryData['objectId'])
        return IdbGenericSqlQueryBuilder.generateSqlGenericDeleteItem(queryData)

    ################################################################################
    # IDB Storage Item                                                             #
    ################################################################################

    @staticmethod
    def generateSqlAddStorageItem(queryData: dict) -> str:
        return IdbGenericSqlQueryBuilder.generateSqlGenericPutItem(queryData)

    @staticmethod
    def generateSqlEditItem(queryData: dict) -> str:
        if 'id' in queryData and isinstance(queryData['id'], int):
            queryData['dbTablePk'] = sql.SQL(str(queryData['id']))
        return IdbGenericSqlQueryBuilder.generateSqlGenericUpdateItem(queryData)

    @staticmethod
    def generateSqlDeleteItem(queryData: dict) -> str:
        if 'id' in queryData and isinstance(queryData['id'], int):
            queryData['dbTablePk'] = sql.SQL(str(queryData['id']))
        return IdbGenericSqlQueryBuilder.generateSqlGenericDeleteItem(queryData)

    @staticmethod
    def generateSqlDeleteItemsByObjectId(queryData: dict) -> str:
        queryData['dbTableColumnPk'] = "oid"
        if 'oid' in queryData and isinstance(queryData['oid'], str):
            queryData['dbTablePk'] = sql.Literal(queryData['oid'])
        return IdbGenericSqlQueryBuilder.generateSqlGenericDeleteItem(queryData)

    ################################################################################
    # IDB Storage General                                                          #
    ################################################################################

    @staticmethod
    def generateSqlCountTable(queryData: dict) -> str:
        queryData['businessDbId'] = queryData['account']
        queryData['dbTableName'] = queryData['dbTableName'].format(**queryData)
        queryData['dbTableNameIdentifier'] = sql.Identifier(queryData['dbTableName'])
        queryData = IdbGenericSqlQueryBuilder.generateSqlGenericTableCondition(queryData)
        return IdbGenericSqlQueryBuilder.generateSqlCountAllItems(queryData)

    @staticmethod
    def generateSqlFindTable(queryData: dict) -> str:
        return IdbGenericSqlQueryBuilder.generateSqlGenericFindItems(queryData)

################################################################################
#                                End of file                                   #
################################################################################
