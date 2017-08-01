#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Sqlite Query Builder"""

import sqlite3

from configuration import config


class Query:
    def __init__(self):
        pass

    def build(self, query, definition, values=None, aggregate=None, where=None):
        """
        Builds a sql query from definition
        :param query: crudt (create, read, update, delete, table)
        :param definition: table model definition
        :param values: valid with update query sql, generates sql with key=value pairs
        :param aggregate: aggregates to  be returned
        :param where: valid with read-, update- and delete query - clause limits the result set
        :return: str
        """
        query = query.lower()[0]

        if query not in ["c", "r", "u", "d", "t"]:
            return "ERROR - UNSUPPORTED TYPE"
        if query in ["r", "u", "d"] and not values or not where:
            return "ERROR - MISSING VALUES OR SELECT CLAUSE"
        if query in ["u", "d"] and not where:
            return "ERROR - DANGEROUS QUERY DETECTED. SPECIFY CLAUSE TO AVOID DAMAGE."

        # insert query
        if query == "c":
            result = self._build_create(definition, values)
            return result

        # select query / aggregate query
        if query == "r":
            result = self._build_select(definition, aggregate, where)
            return result

        # update query
        if query == "u":
            result = self._build_update(definition, values, where)
            return result

        # delete query
        if query == "d":
            result = self._build_delete(definition, where)
            return result

        # create table query
        if query == "t":
            result = self._build_table(definition)
            return result

    def execute(self, query):
        """Execute a query and return the result"""
        db = sqlite3.connect(config.DBPATH)
        with db:
            result = db.execute(query)
            db.commit()
            print("{}".format(result))

    def _build_create(self, definition, values=None):
        sqlf = ""
        sqlv = ""
        name = definition["name"]
        last_f_idx = len(definition["fields"])

        if values:
            for idx, kv in enumerate(values):
                if idx == last_f_idx:
                    sqlf = sqlf + "{}".format(kv[0])
                    sqlv = sqlv + "{}".format(kv[1])
                else:
                    sqlf = sqlf + "{}, ".format(kv[0])
                    sqlv = sqlv + "{}, ".format(kv[1])
            return "INSERT INTO {} ({}) VALUES ({});".format(name, sqlf, sqlv).replace("  ", " ")
        else:
            for idx, f in enumerate(definition["fields"]):
                if idx == last_f_idx:
                    sqlf = sqlf + "?"
                else:
                    sqlf = sqlf + "?, "
            return "INSERT INTO {} VALUES ({});".format(name, sqlf).replace("  ", " ")

    def _build_delete(self, definition, where):
        sqlw = ""
        name = definition["name"]
        last_w_idx = len(where)
        # where field operator value
        for idx, kv in enumerate(where):
            value = kv[1]
            if type(value) == str:
                value = "'" + value + "'"
            if idx == last_w_idx:
                sqlw = sqlw + " {} {} {}".format(kv[0], value, kv[2])
            else:
                if len(kv) == 4:
                    sqlw = sqlw + " {} {} {} {}".format(kv[0], value, kv[2], kv[3].upper())
                else:
                    sqlw = sqlw + " {} {} {}".format(kv[0], value, kv[2])

        return "DELETE FROM {} WHERE {};".format(name, sqlw).replace("  ", " ")

    def _build_select(self, definition, aggregate, where):
        sqla = ""
        sqlw = ""
        name = definition["name"]
        # aggregate list values
        if aggregate:
            aggregate_idx = len(aggregate)
            for idx, a in enumerate(aggregate):
                if idx == aggregate_idx:
                    sqla = sqla + "{}".format(a)
                else:
                    sqla = sqla + "{}, ".format(a)
        # where field operator value
        if where:
            select_idx = len(where)
            for idx, kv in enumerate(where):
                if idx == select_idx:
                    sqlw = sqlw + " {} {} {}".format(kv[0], kv[1], kv[2])
                else:
                    if len(kv) == 4:
                        sqlw = sqlw + " {} {} {} {}".format(kv[0], kv[1], kv[2], kv[3])
                    else:
                        sqlw = sqlw + " {} {} {}".format(kv[0], kv[1], kv[2])

        if sqla and sqlw:
            # select aggregated values where
            return "SELECT {} FROM {} WHERE {};".format(sqla, name, sqlw).replace("  ", " ")
        elif sqla and not sqlw:
            # select aggregated values
            return "SELECT {} FROM {};".format(sqla, name).replace("  ", " ")
        elif sqlw and not sqla:
            # select everything where
            return "SELECT * FROM {} WHERE {};".format(name, sqlw).replace("  ", " ")
        else:
            # just select everything
            return "SELECT * FROM {};".format(name).replace("  ", " ").replace("  ", " ")

    def _build_table(self, definition):
        sqlt = ""
        name = definition["name"]
        last_f_idx = len(definition["fields"])
        for idx, kv in enumerate(zip(definition["fields"], definition["types"])):
            if idx == last_f_idx:
                sqlt = sqlt + "{} {}".format(kv[0], kv[1])
            else:
                sqlt = sqlt + "{} {}, ".format(kv[0], kv[1])

        return "CREATE TABLE IF NOT EXISTS {} ({});".format(name, sqlt).replace("  ", " ")

    def _build_update(self, definition, values, where):
        sqlfv = ""
        sqlw = ""
        name = definition["name"]
        last_f_idx = len(definition)
        last_w_idx = len(where)
        # field=value part
        for idx, kv in enumerate(values):
            value = kv[1]
            if type(value) == str:
                value = "'" + value + "'"
            if idx == last_f_idx:
                sqlfv = sqlfv + "{}={}".format(kv[0], value)
            else:
                sqlfv = sqlfv + "{}={}, ".format(kv[0], value)
        # where field operator value
        for idx, kv in enumerate(where):
            value = kv[1]
            if type(value) == str:
                value = "'" + value + "'"
            if idx == last_w_idx:
                sqlw = sqlw + " {} {} {}".format(kv[0], value, kv[2])
            else:
                if len(kv) == 4:
                    sqlw = sqlw + " {} {} {} {}".format(kv[0], value, kv[2], kv[3].upper())
                else:
                    sqlw = sqlw + " {} {} {}".format(kv[0], value, kv[2])

        return "UPDATE {} SET {} WHERE {};".format(name, sqlfv, sqlw).replace("  ", " ")
