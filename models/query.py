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
    def build(self, query_type, model_def, update=None, aggregate_list=None, where=None, sort_order=None):
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
        :type aggregate_list: iterable ["sum(column) AS 'expression'", "sum(column) AS 'expression'" ....]
        :param aggregate_list: aggregates to  be returned
        :type where: iterable [("field", "operator", "value", "and/or"), (("field", "operator", "value"))]]
        :param where: valid with read-, update- and delete query
        :type sort_order: str
        :param sort_order: asc or desc
        :return: str
        """
        querytype = query_type.upper()
        if querytype not in ["CREATE", "DELETE", "DROP", "INSERT", "SELECT", "UPDATE"]:
            return "ERROR! Unsupported type: {}, {}".format(querytype, model_def["name"])

        if querytype == ["DELETE"]:
            if not where:
                return "ERROR! Missing 'where' for: {}, {}".format(querytype, model_def["name"])

        if querytype == ["UPDATE"]:
            if not where or not update:
                return "ERROR! Missing 'update' or 'where' for: {}, {}".format(querytype, model_def["name"])

        if sort_order:
            sort_order = sort_order.upper()
            if not sort_order == "ASC" or not sort_order == "DESC":
                sort_order = None

        # build create table query
        if querytype == "CREATE":
            return create_query(model_def)

        # build delete row query
        if querytype == "DELETE":
            return delete_query(model_def, where)

        # builds drop table query
        if querytype == "DROP":
            return drop_query(model_def)

        # build insert row query
        if querytype == "INSERT":
            return insert_query(model_def)

        # build select row query
        if querytype == "SELECT":
            return select_query(model_def, aggregate_list, where, sort_order)

        # build update row query
        if querytype == "UPDATE":
            return update_query(model_def, update, where)

    def execute(self, sql_query, values=None):
        """Execute a query and return the result"""
        print("query -> execute -> begin")
        print("q: {}".format(sql_query))
        print("v: {}".format(values))
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
                return False, e
        print("query -> execute -> exit")
        print("r: {}".format(result))
        return True, result

    def values_to_arg(self, values):
        # move id from first to last element
        work = list(values)
        rowid = work[0]
        work = work[1:]
        work.append(rowid)
        work = tuple(work)
        return work
