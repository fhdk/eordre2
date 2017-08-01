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
    def __init__(self):
        """Initialize product class"""
        self.model = {
            "name": "product",
            "fields": ("sku", "name1", "name2", "name3", "item",
                       "price", "d2", "d4", "d6", "d8", "d12", "d24", "d48", "d96", "min", "net", "group"),
            "types": ("TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "TEXT")}
        self.products = []
        self.product = {}

    def clear(self):
        self.product = {}
        self.products = []

    @property
    def product_list(self):
        try:
            _ = self.products[0]
        except IndexError:
            self.load_()
        return self.products

    def drop_table(self):
        """Drop the product table
        The table can be safely recreated.
        An internal pointer to a specific product id is not used as orderline will contain the product sku etc
        This approach also eliminates and outstanding issue with deprecated product
        """
        self.product = []
        dbfn.recreate_table("product")

    def insert_(self, values):
        """Insert a product in database"""
        sql = "INSERT INTO product VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        if not type(values) == list:
            values = list(values)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
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
                self.products = [dict(zip(self.model["fields"], row)) for row in products]
            else:
                self.products = []
