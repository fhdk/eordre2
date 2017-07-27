#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""productsNg class"""

import sqlite3

from configuration import config
from util import dbtablefn


# noinspection PyMethodMayBeStatic
class Product:
    # last_mod -> _invenprices.txt
    # sample content: 2017-06-22 09:15:30
    # __invenprices.txt
    def __init__(self):
        """Initialize products class"""
        # model for zipping dictionary
        self.model = (
            "sku", "name1", "name2", "name3", "item",
            "price", "d2", "d4", "d6", "d8", "d12", "d24", "d48", "d99", "min", "net", "group")
        self.__products = []
        self.__product = {}

    @property
    def productslist(self):
        try:
            _ = self.__products[0]
        except IndexError:
            self.load_()
        return self.__products

    def drop_table(self):
        """Drop the products table
        The table can be safely recreated.
        An internal pointer to a specific products id is not used as orderlines will contain the products sku etc
        This approach also eliminates and outstanding issue with deprecated products
        """
        self.__products = []
        tablename = "products"
        dbtablefn.drop_table(tablename)
        dbtablefn.create_table(tablename)

    def insert_(self, values):
        """Insert a products in database"""
        sql = "INSERT INTO products (sku, name1, name2, name3, item, " \
              "price, d2, d4, d6, d8, d12, d24, d48, d96, min, net, groupid) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, values)
            db.commit()

    def load_(self):
        """Load products list"""
        sql = "SELECT * FROM products;"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql)
            products = cur.fetchall()
            if products:
                self.__products = [dict(zip(self.model, row)) for row in products]
