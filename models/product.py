#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""product module"""

from configuration import config
from models.query import Query

B_COLOR = "\033[0;35m"
E_COLOR = "\033[0;m"

__module__ = "product"


def printit(string):
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


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
            "id": "product_id",
            "fields": ("product_id", "sku", "name1", "name2", "name3", "item", "price", "d2", "d4", "d6", "d8", "d12",
                       "d24", "d48", "d96", "min", "net", "groupid"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0",
                      "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0",
                      "REAL DEFAULT 0", "TEXT")}
        self._products = []
        self._product = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_PRODUCT:
                printit(" ->table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))

    @property
    def current(self):
        """
        Return active product
        """
        return self._product

    @current.setter
    def current(self, product_id):
        """
        Set current product
        Args:
            product_id:
        """
        self.by_id(product_id)

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
            self.all()
        return self._products

    def all(self):
        """
        Load product list
        """
        sql = self.q.build("select", self.model)

        if config.DEBUG_PRODUCT:
            printit(" ->all\n"
                    "  ->sql: {}".format(sql))

        success, data = self.q.execute(sql)

        if config.DEBUG_PRODUCT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success and data:
            self._products = [dict(zip(self.model["fields"], row)) for row in data]
        else:
            self._products = []

    def by_id(self, product_id):
        """
        Set current product
        :param product_id:
        """
        filters = [("product_id", "=")]
        values = (product_id,)
        sql = self.q.build("select", self.model, filteron=filters)
        success, data = self.q.execute(sql, values)
        if success:
            self._product = dict(zip(self.model["fields"], data[0]))
        else:
            self._product = {}

    def clear(self):
        """
        Clear internal variables
        """
        self._product = {}
        self._products = []

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
            printit("{}\n"
                    " ->insert\n"
                    "  -> values"
                    "  ->sql: {}".format(values, sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_PRODUCT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success and data:
            return data
        return False

    def recreate_table(self):
        """
        Drop and init_detail table
        """
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
        self.clear()
