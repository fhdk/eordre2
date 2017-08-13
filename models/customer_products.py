#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Customer products module"""

from models.query import Query
from models.visit import Visit

B_COLOR = "\033[0;33m"
E_COLOR = "\033[0;m"
DBG = True
__module__ = "customer_product"


def printit(string):
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class CustomerProduct:
    """
    CustomerProduct class
    """

    def __init__(self):
        """
        Initialize CustomerProduct class
        """
        self.model = {
            "name": "cp",
            "id": "cp_id",
            "fields": ("cp_id", "c_id", "item", "sku", "pcs"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "TEXT NOT NULL",
                      "TEXT NOT NULL", "INTEGER DEFAULT 0")
        }
        self._products = []
        self._product = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if DBG:
                printit(" ->cp table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))

    @property
    def cp_list(self):
        return self._products

    @cp_list.setter
    def cp_list(self, c_id):
        """
        Load customers into primary list
        """
        self.load(c_id)

    def clear(self):
        """
        Clear internal variables
        """
        self._product = {}
        self._products = []

    def add(self, c_id, item, sku, pcs):
        """
        Create a new customer
        Args:
            c_id:
            item:
            sku:
            pcs:
        Returns:
            bool
        """
        self.insert((None, c_id, item, sku, pcs))
        self.load(c_id)

    def insert(self, values):
        """
        Insert a new current
        Args:
            values:
        Returns:
            rowid
        """
        sql = self.q.build("insert", self.model)
        if DBG:
            printit(" ->insert\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(str(values), sql))
        success, data = self.q.execute(sql, values=values)
        if DBG:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return data
        return False

    def load(self, c_id):
        """
        Load products
        Returns:
            bool
        """
        filters = [("c_id", "=")]
        values = (c_id,)
        sql = self.q.build("select", self.model, filters=filters)
        if DBG:
            printit(" ->load\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        success, data = self.q.execute(sql)
        if DBG:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success:
            try:
                self._products = [dict(zip(self.model["fields"], row)) for row in data]
                return True
            except IndexError:
                self._product = {}
                self._products = []
        return False

    def refresh(self, c_id):
        """
        Refresh customers product list
        Args:
            c_id
        Returns:
            bool
        """
        # select visit_id from visit where customer_id = c_id
        #
        # select detail.sku, sum(pcs) as pcs, product.item
        # from detail
        # inner join product on product.sku = detail.sku
        # where visit_id in (visit_id, visit_id, visit_id)
        # group by detail.sku;
        visit = Visit()
        selection = ("visit_id",)
        filters = [("c_id", "=")]
        values = (c_id,)
        sql = self.q.build("select", visit.model, selection=selection, filters=filters)
        if DBG:
            printit(" ->lookup_by_id\n"
                    "  ->selection: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(selection, filters, str(values), sql))
        success, data = self.q.execute(sql, values=values)
        if DBG:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data[0]))
        if success:
            try:
                v_ids = data[0]
                sql = "SELECT detail.sku, sum(pcs) AS pcs, product.item FROM detail " \
                      "INNER JOIN product ON product.sku = detail.sku " \
                      "WHERE visit_id IN ? GROUP BY detail.sku"
                success, data = self.q.execute(sql, v_ids)
                if success:
                    try:
                        self._products = [dict(zip(self.model["fields"], row)) for row in data]
                    except IndexError:
                        pass
                return True
            except IndexError:
                self._product = {}
        return False

    def recreate_table(self):
        """
        Drop and create table
        """
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
        self.clear()

    def update(self):
        """
        Update customer
        Returns:
            bool
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._product.values())
        sql = self.q.build("update", self.model, update=fields, filters=filters)
        if DBG:
            printit(" ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(fields, filters, str(values), sql))
        success, data = self.q.execute(sql, values=values)
        if DBG:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return True
        return False
