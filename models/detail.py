#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Visit details module
"""

import csv

from configuration import config
from models.query import Query
from util import utils

B_COLOR = "\033[1;30m"
E_COLOR = "\033[0;m"
DBG = False

__module__ = "detail"


def printit(string):
    """Print a variable string for debug purposes"""
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class Detail:
    """
    Visit details class
    """

    def __init__(self):
        """
        Initialize Saleine class
        """
        self.model = {
            "name": "detail",
            "id": "detail_id",
            "fields": ("detail_id", "visit_id", "pcs", "sku", "text", "price", "sas", "discount",
                       "linetype", "extra"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "INTEGER DEFAULT 0",
                      "TEXT", "TEXT", "REAL", "INTEGER DEFAULT 0", "REAL DEFAULT 0", "TEXT", "TEXT")
        }
        self._details = []
        self._detail = {}
        self._csv_field_count = 8
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_SALELINE:
                printit(" ->table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))

    @property
    def active(self):
        """
        Single current detail
        Returns:
             current
        """
        return self._detail

    @active.setter
    def active(self, detail_id):
        """
        Set the current detail
        Args:
            detail_id:
        """
        try:
            d_id = self._detail["detail_id"]
            if not d_id == detail_id:
                self.find(detail_id=detail_id)
        except KeyError:
            self.find(detail_id=detail_id)

    @property
    def csv_field_count(self):
        """The number of fields expected on csv import"""
        return self._csv_field_count

    @property
    def details_list(self):
        """
        Visit details list
        Returns:
            List of details for a current
        """
        return self._details

    @details_list.setter
    def details_list(self, visit_id):
        """
        Visit details setter. Load details for visit_id
        Args:
            visit_id:
        """
        try:
            vid = self._details[0]["visit_id"]
            if not vid == visit_id:
                self.load(visit_id=visit_id)
        except (IndexError, KeyError):
            self.load(visit_id)

    def add(self, visit_id, line_type):
        """
        Initialize a new detail with visitid
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
        self._detail = {}
        self._details = []

    def delete(self, detail_id):
        """
        Delete the detail
        Args:
            detail_id:
        Returns:
            bool
        """
        filters = [(self.model["id"], "=")]
        values = (detail_id,)
        sql = self.q.build("delete", self.model, filters=filters)
        if config.DEBUG_SALELINE:
            printit(" ->delete\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        success, data = self.q.execute(sql, values)
        if config.DEBUG_SALELINE:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return True
        return False

    def find(self, detail_id):
        """
        Find the specified detail
        Args:
            detail_id:
        Returns:
            bool
        """
        filters = [(self.model["id"], "=")]
        values = (detail_id,)
        sql = self.q.build("select", self.model, filters=filters)
        if config.DEBUG_SALELINE:
            printit(" ->all\n"
                    "  ->sql: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}".format(sql, filters, values))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_SALELINE:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success:
            try:
                self._detail = dict(zip(self.model["fields"], data[0]))
                return True
            except IndexError:
                self._detail = {}
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
        if config.DEBUG_SALELINE:
            printit("  ->values: {}".format(new_row))
        self.insert(new_row)

    def insert(self, values):
        """
        Insert row
        Args:
            values:
        Returns:
            bool
        """
        sql = self.q.build("insert", self.model)
        if config.DEBUG_SALELINE:
            printit(" ->insert\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(sql, values))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_SALELINE:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return data
        return False

    def load(self, visit_id):
        """
        Load details for visit_id
        Args:
            visit_id:
        Returns:
            bool
        """
        filters = [("visit_id", "=")]
        values = (visit_id,)
        sql = self.q.build("select", self.model, filters=filters)
        if config.DEBUG_SALELINE:
            printit(" ->all\n"
                    "  ->sql: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}".format(sql, filters, values))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_SALELINE:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success:
            try:
                self._details = [dict(zip(self.model["fields"], row)) for row in data]
                self._detail = self._details[0]
                return True
            except (IndexError, KeyError):
                self._detail = {}
                self._details = []
        return False

    def recreate_table(self):
        """
        Drop and creete table
        """
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
        self.clear()

    def save_all(self):
        """
        Write the list of details to database
        """
        for detail in self._details:
            if detail[self.model["id"]] is None:
                self.insert(detail.values())
            else:
                self._detail = detail
                self.update()

    def update(self):
        """
        Write the current detail to database
        Returns:
            bool
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._detail.values())
        sql = self.q.build("update", self.model, update=fields, filters=filters)
        if sql.startswith("ERROR"):
            printit("{}".format(sql))
            return False
        if DBG:
            printit(" ->all\n"
                    "  ->sql: {}\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}".format(sql, fields, filters, values))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_SALELINE:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return data
        return False
