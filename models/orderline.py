#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Orderline class"""

import csv
import sqlite3

from configuration import config
from util import dbtablefn


class OrderLine:
    def __init__(self):
        """Initialize OrderLine class"""
        # model for zipping dictionary
        self.model = ("lineid", "orderid", "pcs", "sku", "infotext", "price", "sas", "discount")
        self.__orderlines = []
        self.__orderline = {}

    def import_csv(self, filename, headers=False):
        """Import orderlines from file
        :param filename:
        :param headers:
        """
        sql = "INSERT INTO " \
              "orderlines (lineid, orderid, pcs, sku, infotext, price, sas, discount) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        tablename = "orderline"
        dbtablefn.drop_table(tablename)
        dbtablefn.create_table(tablename)
        conn = sqlite3.connect(config.DBPATH)
        filename.encode("utf8")
        with conn:
            with open(filename) as csvdata:
                reader = csv.reader(csvdata)
                line = 0
                for row in reader:
                    line += 1
                    if headers and line == 1:
                        continue
                    processed = [row[0], row[1], row[2], row[3].strip(), row[4].strip(), row[5], row[6], row[7]]
                    conn.execute(sql, processed)

        conn.commit()
