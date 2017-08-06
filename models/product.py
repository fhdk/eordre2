#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""productNg class"""

from configuration import config
from models.query import Query


# noinspection PyMethodMayBeStatic
class Product:
    """
    Product
    """

    def __init__(self):
        """
        Initialize product class
        """
        self.model = {
            "name": "product",
            "id": "productid",
            "fields": ("productid", "sku", "name1", "name2", "name3", "item", "price", "d2", "d4", "d6", "d8", "d12",
                       "d24", "d48", "d96", "min", "net", "groupid"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0",
                      "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0",
                      "REAL DEFAULT 0", "TEXT")}
        self._products = []
        self._product = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_PRODUCT:
                print("\033[1;34m{}\n ->table\n  ->success: {}\n  ->data: {}\033[0;m".format(
                    self.model["name"], success, data))

    def clear(self):
        """
        Clear internal variables
        """
        self._product = {}
        self._products = []

    @property
    def product_list(self):
        """
        ProductList
        Returns:
            List of products
        """
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
        self.recreate_table()

    def insert(self, values):
        """
        Insert a product in database
        Args:
            values:
        """
        values = list(values)
        values[0:0] = [None]
        values = tuple(values)

        sql = self.q.build("insert", self.model)

        if config.DEBUG_PRODUCT:
            print("\033[1;34m{}\n ->insert\n  ->sql: {}".format(self.model["name"], sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_PRODUCT:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            return data
        return False

    def load(self):
        """
        Load product list
        """
        # build query and execute
        sql = self.q.build("select", self.model)

        if config.DEBUG_PRODUCT:
            print("\033[1;34m{}\n ->load\n  ->sql: {}".format(self.model["name"], sql))

        success, data = self.q.execute(sql)

        if config.DEBUG_PRODUCT:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            self._products = [dict(zip(self.model["fields"], row)) for row in data]
        else:
            self._products = []

    def recreate_table(self):
        """
        Drop and create table
        """
        # build query and execute
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
