#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Sqlite Query Builder"""

import sqlite3

from configuration import config
from models.builders.delete_query import delete_query
from models.builders.insert_query import insert_query
from models.builders.select_query import select_query
from models.builders.update_query import update_query
from models.builders.create_query import create_query
from models.builders.drop_query import drop_query


class Query:
    def build(self, query_type, model_def, update_list=None, aggregate_list=None, where_list=None, sort_order=None):
        """
        Builds a sql query from definition
        :param query_type: add(table), insert, select, update, delete)
        :type query_type: str "add"
        :param model_def: table model definition
        :type model_def: object
            {"name": ("name" ...),
             "fields": ("field" ...),
             "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT" ...)}
        :param update_list: key:value pairs
        :type update_list: iterable ("field", "field" ...)
        :type aggregate_list: iterable ["sum(column) AS 'expression'", "sum(column) AS 'expression'" ....]
        :param aggregate_list: aggregates to  be returned
        :type where_list: iterable [("field", "operator", "value", "and/or"), (("field", "operator", "value"))]]
        :param where_list: valid with read-, update- and delete query
        :type sort_order: str
        :param sort_order: asc or desc
        :return: str
        """
        querytype = query_type.upper()
        if querytype not in ["CREATE", "DROP", "INSERT", "SELECT", "UPDATE", "DELETE"]:
            return "ERROR - UNSUPPORTED TYPE"
        if querytype in ["UPDATE", "DELETE"] and not where_list:
            return "ERROR - MISSING WHERE CLAUSE"

        if sort_order:
            sort_order = sort_order.upper()
            if not sort_order == "ASC" or not sort_order == "DESC":
                sort_order = None

        # build insert query
        if querytype == "INSERT":
            return insert_query(model_def)

        # build select query
        if querytype == "SELECT":
            return select_query(model_def, aggregate_list, where_list, sort_order)

        # build update query
        if querytype == "UPDATE":
            return update_query(model_def, update_list, where_list)

        # build delete query
        if querytype == "DELETE":
            return delete_query(model_def, where_list)

        # build add table query
        if querytype == "CREATE":
            return create_query(model_def)

        # builds drop table query
        if querytype == "DROP":
            return drop_query(model_def)

    def execute(self, sql_query, value_list=None):
        """Execute a query and return the result"""
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            try:
                if value_list:
                    for item in value_list:
                        cur.execute(sql_query, item)
                else:
                    cur.execute(sql_query)
                db.commit()

                if sql_query.startswith("SELECT"):
                    return True, cur.fetchall()

                if sql_query.startswith("INSERT"):
                    return True, cur.execute("SELECT last_insert_rowid();")

            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                return False, e
