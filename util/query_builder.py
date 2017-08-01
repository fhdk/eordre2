#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Sqlite Query Builder"""


class QueryBuilder:
    def __init__(self):
        pass

    def build(self, query, definition, values=None, where=None):
        """
        Builds a sql query from definition
        :param query: crudt (create table, read, update, delete, table)
        :param definition: table model definition
        :param values: valid with update query sql, generates sql with key=value pairs
        :param where: valid with read-, update- and delete query - clause limits the result set
        :return: str
        """
        sql = ""
        query = query.lower()[0]
        name = definition["name"]
        last_field_idx = len(definition["fields"]) - 1
        last_select_idx = len(where) - 1

        if query not in ["c", "r", "u", "d", "t"]:
            return "ERROR - UNSUPPORTED TYPE"
        if query in ["r", "u", "d"] and not values or not where:
            return "ERROR - MISSING VALUES OR SELECT CLAUSE"
        if query in ["u", "d"] and not where:
            return "ERROR - DANGEROUS QUERY DETECTED. SPECIFY CLAUSE TO AVOID DAMAGE."

        if query == "c":
            if values:
                sqlf = ""
                sqlv = ""
                for idx, kv in enumerate(values):
                    if idx == last_field_idx:
                        sqlf = sqlf + "{}".format(kv[0])
                        sqlv = sqlv + "{}".format(kv[1])
                    else:
                        sqlf = sqlf + "{}, ".format(kv[0])
                        sqlv = sqlv + "{}, ".format(kv[1])
                sql = "INSERT INTO {} ({}) VALUES ({});".format(name, sqlf, sqlv)
            else:
                for idx, f in enumerate(definition["fields"]):
                    if idx == last_field_idx:
                        sql = sql + "?"
                    else:
                        sql = sql + "?, "
                    sql = "INSERT INTO {} VALUES ({});".format(name, sql)

        if query == "r":
            if where:
                for idx, kv in enumerate(where):
                    if idx == last_select_idx:
                        sql = sql + " {}={}".format(kv[0], kv[1])
                    else:
                        if len(kv) == 3:
                            sql = sql + " {}={} {}".format(kv[0], kv[1], kv[2])
                        else:
                            sql = sql + " {}={}".format(kv[0], kv[1])
                sql = "SELECT * FROM {} WHERE {};".format(sql)
            else:
                sql = "SELECT * FROM {};".format(name)

        if query == "u":
            sqlfv = ""
            sqlwhere = ""

            for idx, kv in enumerate(values):
                value = kv[1]
                if type(value) == str:
                    value = "'" + value + "'"
                if idx == last_field_idx:
                    sqlfv = sqlfv + "{}={}".format(kv[0], value)
                else:
                    sqlfv = sqlfv + "{}={}, ".format(kv[0], value)

            for idx, kv in enumerate(where):
                value = kv[1]
                if type(value) == str:
                    value = "'" + value + "'"
                if idx == last_select_idx:
                    sqlwhere = sqlwhere + " {}={}".format(kv[0], value)
                else:
                    if len(kv) == 3:
                        sqlwhere = sqlwhere + " {}={} {}".format(kv[0], value, kv[2].upper())
                    else:
                        sqlwhere = sqlwhere + " {}={}".format(kv[0], value)

            sql = "UPDATE {} SET {} WHERE {};".format(name, sqlfv, sqlwhere)

        if query == "d":
            sqlwhere = ""
            for idx, kv in enumerate(where):
                value = kv[1]
                if type(value) == str:
                    value = "'" + value + "'"
                if idx == last_select_idx:
                    sqlwhere = sqlwhere + " {}={}".format(kv[0], value)
                else:
                    if len(kv) == 3:
                        sqlwhere = sqlwhere + " {}={} {}".format(kv[0], value, kv[2].upper())
                    else:
                        sqlwhere = sqlwhere + " {}={}".format(kv[0], value)

            sql = "DELETE FROM {} WHERE {};".format(name, sqlwhere)

        if query == "t":
            for idx, kv in enumerate(zip(definition["fields"], definition["types"])):
                if idx == last_field_idx:
                    sql = sql + "{} {}".format(kv[0], kv[1])
                else:
                    sql = sql + "{} {}, ".format(kv[0], kv[1])

            sql = "CREATE TABLE IF NOT EXISTS {} ({});".format(name, sql)

        return sql.replace("  ", " ")
