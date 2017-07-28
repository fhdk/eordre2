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
        self.model = ("lineid", "orderid", "pcs", "sku", "infotext", "price", "sas", "discount")
        self.__orderlines = []
        self.__orderline = {}

    def csv_import(self, filename, headers=False):
        """Import orderline from file
        :param filename:
        :param headers:
        """
        dbfn.recreate_table("orderline")
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata)
            line = 0
            for row in reader:
                line += 1
                if headers and line == 1:
                    continue
                processed = [row[0], row[1], row[2], row[3].strip(), row[4].strip(), row[5], row[6], row[7]]
                self.insert_values(processed)

    def insert_values(self, values):
        sql = "INSERT INTO orderline (" \
              "lineid, orderid, pcs, sku, infotext, price, sas, discount) " \
              "VALUES (" \
              "?, ?, ?, ?, ?, ?, ?, ?);"
        if not values:
            values = list(self.__orderline.values())
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()
