#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Sqlite Query Builder"""

import sqlite3

from configuration import config
from models.builders.build_delete_query import delete_query
from models.builders.build_insert_query import insert_query
from models.builders.build_select_query import select_query
from models.builders.build_update_query import update_query
from models.builders.create_query import create_query
from models.builders.build_drop_query import drop_query


class Query:
    """
    """
    def build(self, query_type, model_def, update=None, aggregates=None, filteron=None, sort_order=None):
        """
        Builds a sql query from definition
        :param query_type: add(table), insert, select, update, delete)
        :type query_type: str "add"
        :param model_def: table model definition
        :type model_def: object
            {"name": ("name" ...),
             "fields": ("field" ...),
             "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT" ...)}
        :param update: fields to update
        :type update: iterable ("field", "field" ...)
        :type aggregates: iterable ["sum(column) AS 'expression'", "sum(column) AS 'expression'" ....]
        :param aggregates: aggregates to  be returned
        :type filteron: iterable [("field", "operator", "value", "and/or"), (("field", "operator", "value"))]]
        :param where: valid with read-, update- and delete query
        :type sort_order: str
        :param sort_order: asc or desc
        :return: str
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
            return create_query(model_def)

        # build delete row query
        if querytype == "DELETE":
            return delete_query(model_def, filteron)

        # builds drop table query
        if querytype == "DROP":
            return drop_query(model_def)

        # build insert row query
        if querytype == "INSERT":
            return insert_query(model_def)

        # build select row query
        if querytype == "SELECT":
            return select_query(model_def, aggregates, filteron, sort_order)

        # build update row query
        if querytype == "UPDATE":
            return update_query(model_def, update, filteron)

    def execute(self, sql_query, values=None):
        """Execute a query and return the result"""
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

        Args:
            values:

        Returns:

        """
        # move id from first to last element
        work = list(values)
        rowid = work[0]
        work = work[1:]
        work.append(rowid)
        work = tuple(work)
        return work

    def exist_table(self, table):
        """Check database if tablename exist

        Args:
            table: 
        """
        statement = "select name from sqlite_master " \
                    "where type='{}' and name='{}';".format("table", table)

        success, data = self.execute(statement)
        if config.DEBUG_QUERY:
            print("{} -> exist_table\nsuccess: {}\ndata   : {}".format("QUERY", success, data))
        if data:
            return True
        return False
