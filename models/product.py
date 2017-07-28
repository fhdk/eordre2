#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""productNg class"""

import sqlite3

from configuration import config
from util import dbfn


# noinspection PyMethodMayBeStatic
class Product:
    # last_mod -> _invenprices.txt
    # sample content: 2017-06-22 09:15:30
    # __invenprices.txt
    def __init__(self):
        """Initialize product class"""
        # model for zipping dictionary
        self.model = (
            "sku", "name1", "name2", "name3", "item",
            "price", "d2", "d4", "d6", "d8", "d12", "d24", "d48", "d99", "min", "net", "group")
        self.__product_list = []
        self.__product = {}

    @property
    def productlist(self):
        try:
            _ = self.__product_list[0]
        except IndexError:
            self.load_()
        return self.__product_list

    def drop_table(self):
        """Drop the product table
        The table can be safely recreated.
        An internal pointer to a specific product id is not used as orderline will contain the product sku etc
        This approach also eliminates and outstanding issue with deprecated product
        """
        self.__product = []
        dbfn.recreate_table("product")

    def insert_(self, values):
        """Insert a product in database"""
        sql = "INSERT INTO product (sku, name1, name2, name3, item, " \
              "price, d2, d4, d6, d8, d12, d24, d48, d96, min, net, groupid) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, values)
            db.commit()

    def load_(self):
        """Load product list"""
        sql = "SELECT * FROM product;"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql)
            products = cur.fetchall()
            if products:
                self.__product_list = [dict(zip(self.model, row)) for row in products]
            else:
                self.__product_list = []
