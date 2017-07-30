#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Orderline class"""

import csv
import sqlite3

from configuration import config
from util import dbfn


class OrderLine:
    def __init__(self):
        """Initialize OrderLine class"""
        # model for zipping dictionary
        self.model = ("lineid", "visitid", "pcs", "sku", "infotext", "price", "sas", "discount")
        self.__order_lines = []
        self.__current_line = {}

    @property
    def orderlines_list(self):
        return self.__order_lines

    @orderlines_list.setter
    def orderlines_list(self, visitid):
        try:
            _ = self.__order_lines[0]
        except IndexError:
            self.load_(visitid)

    def clear(self):
        self.__current_line = {}
        self.__order_lines = []

    def create_(self, visit_id):
        """Create a new orderline on visitid"""
        # create new with empty values
        values = (None, visit_id, None, "", "", None, None, None)
        self.insert_values(values)
        self.__current_line = dict(zip(self.model, values))

    def csv_import(self, filename, headers=False):
        """Import orderline from file
        :param filename: csv file
        :param headers: flag first row as fieldnames
        """
        csv_field_count = 8
        dbfn.recreate_table("orderline")
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata)
            line = 0
            for row in reader:
                if not len(row) == csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # sanitize line
                processed = [row[0], row[1], row[2], row[3].strip(), row[4].strip(), row[5], row[6], row[7]]
                self.insert_values(processed)
            return True

    def insert_values(self, values=None):
        sql = "INSERT INTO orderline VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        # sanitize values
        if not values:
            try:
                values = self.__current_line.values()
            except KeyError:
                return
        if not type(values) == list or type(values) == tuple:
            values = list(values)
        # db insert
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()

    def load_(self, visitid):
        """Load orderlines"""
        sql = "SELECT * FROM orderline WHERE visitid=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            orderlines = cur.execute(sql, list(visitid))
            if orderlines:
                self.orderlines_list = [dict(zip(self.model, row)) for row in orderlines]

    def update_(self, values):
        """Update orderline"""
        sql = "UPDATE orderline " \
              "SET " \
              "lineid=?, visitid=?, pcs=?, sku=?, infotext=?, price=?, sas=?, discount=? " \
              "WHERE lineid=?"
        if not type(values) == list or type(values) == tuple:
            values = list(values)
        values += [values[0]]
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()
