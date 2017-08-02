#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Orderline class"""

import csv

from util import dbfn, utils
from util.query import Query


class OrderLine:
    def __init__(self):
        """Initialize OrderLine class"""
        self.model = {
            "name": "orderline",
            "idfield": "lineid",
            "fields": ("lineid", "visitid", "pcs", "sku", "infotext", "price", "sas", "discount"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER", "INTEGER", "TEXT", "TEXT", "REAL", "INTEGER", "REAL")
        }
        self._order_lines = []
        self._order_line = {}
        self.csv_field_count = 8
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def orderlines_list(self):
        return self._order_lines

    @orderlines_list.setter
    def orderlines_list(self, visitid):
        try:
            _ = self._order_lines[0]
        except IndexError:
            self.load(visitid)

    def clear(self):
        self._order_line = {}
        self._order_lines = []

    def create(self, visit_id):
        """Create a new orderline on visitid"""
        # add new with empty values
        values = (None, visit_id, None, "", "", None, None, None)
        self.insert_values(values)
        self._order_line = dict(zip(self.model["fields"], values))

    def csv_import(self, filename, headers=False):
        """Import orderline from file
        :param filename: csv file
        :param headers: flag first row as fieldnames
        """
        csv_field_count = 8
        dbfn.recreate_table("orderline")
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                if not len(row) == csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # translate bool text to integer col 6
                row[6] = utils.bool2int(utils.str2bool(row[6]))
                processed = [row[0], row[1], row[2], row[3].strip(), row[4].strip(), row[5], row[6], row[7]]
                self.insert_values(processed)
            return True

    def insert_values(self, values):
        sql = self.q.build("insert", self.model)
        value_list = values
        if not type(values) == list:
            value_list = list(values)
        self.q.execute(sql, value_list=value_list)

    def load(self, visitid):
        """Load orderlines"""
        where_list = [("visitid", "=")]
        sql = self.q.build("select", self.model, where_list=where_list)
        value_list = [visitid]
        result = self.q.execute(sql, value_list=value_list)
        if result:
            self.orderlines_list = [dict(zip(self.model["fields"], row)) for row in result]

    def update(self, values):
        """Update orderline"""
        update_list = list(self.model["fields"])[1:]
        where_list = [("lineid", "=")]
        value_list = values
        if not type(values) == list:
            value_list = list(values)
        value_list = values.append(value_list[0])[1:]
        sql = self.q.build("update", self.model, update_list=update_list, where_list=where_list)
        self.q.execute(sql, value_list=value_list)
