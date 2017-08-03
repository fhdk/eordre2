#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Sqlite Query Builder"""

import sqlite3

from configuration import config
from models.builders.build_delete_query import build_delete_query
from models.builders.build_insert_query import build_insert_query
from models.builders.build_select_query import build_select_query
from models.builders.build_update_query import build_update_query
from models.builders.build_create_query import build_create_query
from models.builders.build_drop_query import build_drop_query


class Query:
    """
    """

    def build(self, query_type, model_def, update=None, aggregates=None, filteron=None, sort_order=None):
        """
        Builds a sql query from definition

        Args:
            query_type: create(table), drop(table), insert(row), select(row), update(row), delete(row))

            model_def: table model definition
            {"name": ("name" ...), "fields": ("field" ...), "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT" ...)}

            update: fields to update
            ("field", "field" ...)

            aggregates: valid ["sum(column) AS 'expression'", "sum(column) AS 'expression'" ....]

            filteron:  valid for select-, required for update- and delete query
            [("field", "operator", "value", "and/or"), (("field", "operator", "value"))]]

            sort_order: asc or desc

        Returns:
            string with sql query

        """

        querytype = query_type.upper()
        if querytype not in ["CREATE", "DELETE", "DROP", "INSERT", "SELECT", "UPDATE"]:
            return "ERROR! Unsupported type: {}, {}".format(querytype, model_def["name"])

        if querytype == ["DELETE"]:
            if not filteron:
                return "ERROR! Missing 'filteron' for: {}, {}".format(querytype, model_def["name"])

        if querytype == ["UPDATE"]:
            if not filteron or not update:
                return "ERROR! Missing 'update' or 'filteron' for: {}, {}".format(querytype, model_def["name"])

        if sort_order:
            sort_order = sort_order.upper()
            if not sort_order == "ASC" or not sort_order == "DESC":
                sort_order = None

        # build create table query
        if querytype == "CREATE":
            return build_create_query(model_def)

        # build delete row query
        if querytype == "DELETE":
            return build_delete_query(model_def, filteron)

        # builds drop table query
        if querytype == "DROP":
            return build_drop_query(model_def)

        # build insert row query
        if querytype == "INSERT":
            return build_insert_query(model_def)

        # build select row query
        if querytype == "SELECT":
            return build_select_query(model_def, aggregates, filteron, sort_order)

        # build update row query
        if querytype == "UPDATE":
            return build_update_query(model_def, update, filteron)

    def execute(self, sql_query, values=None):
        """
        Execute a query and return the result

        """
        if config.DEBUG_QUERY:
            print("{}->execute->enter\nsql_query: {}\nvalues   :".format("QUERY", sql_query, values))
        # query types: create, delete, insert, select, update
        select = sql_query.startswith("SELECT")
        insert = sql_query.startswith("INSERT")
        db = sqlite3.connect(config.DBPATH)
        with db:
            try:
                result = None
                cur = db.cursor()
                if values:
                    cur.execute(sql_query, values)
                else:
                    cur.execute(sql_query)
                db.commit()
                if select:
                    result = cur.fetchall()
                if insert:
                    result = cur.lastrowid
            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                if config.DEBUG_QUERY:
                    print("{}->execute->exception: {}".format("QUERY", e))
                return False, e
        if config.DEBUG_QUERY:
            print("{}->execute->exit\nresult: {}".format("QUERY", result))

        return True, result

    def values_to_arg(self, values):
        """
        Moves the id field from first to last element
        Args:
            values:

        Returns:
            Value list with id as the last field
        """
        work = list(values)
        rowid = work[0]
        work = work[1:]
        work.append(rowid)
        work = tuple(work)
        return work

    def exist_table(self, table):
        """
        Check database if tablename exist
        Args:
            table:

        Returns:
             bool indicating if table was found
        """
        statement = "select name from sqlite_master " \
                    "where type='{}' and name='{}';".format("table", table)

        success, data = self.execute(statement)
        if config.DEBUG_QUERY:
            print("{} -> exist_table\nsuccess: {}\ndata   : {}".format("QUERY", success, data))
        if data:
            return True
        return False
