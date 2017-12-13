#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# Copyright: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Visit details module
"""

from models.query import Query
from util import utils


__module__ = "order_lines"


class OrderLine:
    """
    Order lines class
    """

    def __init__(self):
        """
        Initialize OrderLines class
        """
        self.model = {
            "name": "orderlines",
            "id": "line_id",
            "fields": ("line_id", "visit_id", "pcs", "sku", "text", "price", "sas", "discount",
                       "linetype", "extra"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "INTEGER DEFAULT 0",
                      "TEXT", "TEXT", "REAL", "INTEGER DEFAULT 0", "REAL DEFAULT 0", "TEXT", "TEXT")
        }
        self._purchase_order_lines = []
        self._purchase_order_line = {}
        self._csv_record_lenght = 8
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def purchase_order_line(self):
        """
        Return the current focused purchase order line
        Returns:
             current
        """
        return self._purchase_order_line

    @purchase_order_line.setter
    def purchase_order_line(self, line_id):
        """
        Set the current focused purchase order line
        Args:
            line_id:
        """
        try:
            d_id = self._purchase_order_line["detail_id"]
            if not d_id == line_id:
                self.find(orderline_id=line_id)
        except KeyError:
            self.find(orderline_id=line_id)

    @property
    def csv_field_count(self):
        """The number of fields expected on csv import"""
        return self._csv_record_lenght

    @property
    def order_lines(self):
        """
        All purchase order lines
        Returns:
            List of details for a purchase order line
        """
        return self._purchase_order_lines

    @order_lines.setter
    def order_lines(self, visit_id):
        """
        Visit details setter. Load purchase order lines for visit_id
        Args:
            visit_id:
        """
        try:
            vid = self.order_lines[0]["visit_id"]
            if not vid == visit_id:
                self.load(visit_id=visit_id)
        except (IndexError, KeyError):
            self.load(visit_id)

    def add(self, visit_id, line_type):
        """
        Initialize a new purchase order line with visitid
        Args:
            visit_id:
            line_type:
        """
        line_type = line_type.upper()
        values = (None, visit_id, "", "", "", "", "", "", line_type, "")
        new_id = self.insert(values)
        self.find(new_id)

    def clear(self):
        """
        Clear internal variables
        """
        self._purchase_order_line = {}
        self.order_lines = []

    def delete(self, orderline_id):
        """
        Delete orderline with id
        Args:
            orderline_id:
        Returns:
            bool
        """
        filters = [(self.model["id"], "=")]
        values = (orderline_id,)
        sql = self.q.build("delete", self.model, filters=filters)
        success, data = self.q.execute(sql, values)
        if success and data:
            return True
        return False

    def find(self, orderline_id):
        """
        Find the the order line with id
        Args:
            orderline_id:
        Returns:
            bool
        """
        filters = [(self.model["id"], "=")]
        values = (orderline_id,)
        sql = self.q.build("select", self.model, filters=filters)
        success, data = self.q.execute(sql, values=values)
        if success:
            try:
                self._purchase_order_line = dict(zip(self.model["fields"], data[0]))
                return True
            except IndexError:
                self._purchase_order_line = {}
        return False

    def import_csv(self, row):
        """
        Translate a csv row
        Args:
            row:
        """
        # translate bool text to integer col 6
        field_6 = utils.bool2int(utils.arg2bool(row[6]))
        new_row = (row[0], row[1], row[2], row[3].strip(), row[4].strip(), row[5], field_6, row[7], "S", None)
        self.insert(new_row)

    def insert(self, values):
        """
        Insert a new orderline with values
        Args:
            values:
        Returns:
            rownumber or None
        """
        sql = self.q.build("insert", self.model)
        success, data = self.q.execute(sql, values=values)
        if success and data:
            return data
        return None

    def load(self, visit_id):
        """
        Load order lines for visit_id
        Args:
            visit_id:
        Returns:
            bool: True on success
        """
        filters = [("visit_id", "=")]
        values = (visit_id,)
        sql = self.q.build("select", self.model, filters=filters)
        success, data = self.q.execute(sql, values=values)
        if success:
            try:
                self.order_lines = [dict(zip(self.model["fields"], row)) for row in data]
                self._purchase_order_line = self.order_lines[0]
                return True
            except (IndexError, KeyError):
                self._purchase_order_line = {}
                self.order_lines = []
        return False

    def recreate_table(self):
        """
        Recrete table and clears internal variables
        """
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
        self.clear()

    def save_all(self):
        """
        Save the list of orderlines
        """
        for order_line in self._purchase_order_lines:
            if order_line[self.model["id"]] is None:
                self.insert(order_line.values())
            else:
                self._purchase_order_line = order_line
                self.update()

    def update(self):
        """
        Update orderline data in database
        Returns:
            rownumber or None
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_update(self._purchase_order_line.values())
        sql = self.q.build("update", self.model, update=fields, filters=filters)
        if sql.startswith("ERROR"):
            return None
        success, data = self.q.execute(sql, values=values)
        if success and data:
            return data
        return None
