#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""productNg class"""

from util import dbfn
from util.query import Query


# noinspection PyMethodMayBeStatic
class Product:
    def __init__(self):
        """Initialize product class"""
        self.model = {
            "name": "product",
            "id": "productid",
            "fields": ("productid", "sku", "name1", "name2", "name3", "item", "price", "d2", "d4", "d6", "d8", "d12",
                       "d24", "d48", "d96", "min", "net", "group"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT","REAL", "REAL",
                      "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "TEXT")}
        self._products = []
        self._product = {}
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    def clear(self):
        self._product = {}
        self._products = []

    @property
    def product_list(self):
        try:
            _ = self._products[0]
        except IndexError:
            self.load()
        return self._products

    def drop_table(self):
        """Drop the product table
        The table can be safely recreated.
        An internal pointer to a specific product id is not used as orderline will contain the product sku etc
        This approach also eliminates and outstanding issue with deprecated product
        """
        self._product = []
        dbfn.recreate_table("product")

    def insert(self, values):
        """Insert a product in database"""
        sql = self.q.build("insert", self.model)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        self.q.execute(sql, value_list=value_list)

    def load(self):
        """Load product list"""
        sql = self.q.build("select", self.model)
        result = self.q.execute(sql)
        if result:
            self._products = [dict(zip(self.model["fields"], row)) for row in result]
        else:
            self._products = []
