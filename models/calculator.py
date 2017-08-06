# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Calculation module
"""

from configuration import config
from models.query import Query


class Calculator:
    """
    Calculator
    """

    def __init__(self):
        """
        Initialize Calculator
        """
        self.model = {
            "name": "calculations",
            "id": "calcid",
            "fields": ("calcid", "calcdate", "reportid", "employeeid", "counted",
                       "new_visit", "new_demo", "new_sale", "new_turnover",
                       "recall_visit", "recall_demo", "recall_sale", "recall_turnover",
                       "sas", "sas_turnover", "visit", "demo", "sale", "turnover",
                       "kmwork", "kmprivate", "workdays", "offdays"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT NOT NULL", "INTEGER NOT NULL", "INTEGER NOT NULL",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "REAL DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "REAL DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "INTEGER DEFAULT 0", "REAL DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0")
        }
        self._totals = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_CALCULATOR:
                print(
                    "\033[1;30m{} ->create table\n  ->success: {}\n  ->data   : {}\033[0;m".format(
                        self.model["name"], success, data))

    @property
    def totals(self):
        """
        Totals
        Returns:
            The current totals
        """
        return self._totals

    def insert(self, values):
        """
        Save values to database and sets totals with the supplied values
        Args:
            values:
        """
        values = list(values)
        values[0:0] = [None]
        values = tuple(values)

        sql = self.q.build("insert", self.model)

        if config.DEBUG_CALCULATOR:
            print("\033[1;30m{} ->insert \n  ->sql: {}\n  ->data: {}".format(self.model["name"], sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CALCULATOR:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            return data
        return False

    def select_by_id(self, calc_id):
        """
        Select by id
        Returns:
            bool indicating totals has been set for the requested id
        """
        filters = [("calcid", "=")]
        values = (calc_id,)

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_CALCULATOR:
            print("\033[1;30m{} ->select_by_id\n  ->sql: {}\n  ->filters: {}\n  ->values: {}".format(
                self.model["name"], sql, filters, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CALCULATOR:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            self._totals = dict(zip(self.model["fields"], data[0]))
            return self._totals
        return False

    def select_by_date_employee(self, workdate, employeeid):
        """
        Select totals for employeeid and workdate

        Args:
            workdate:
            employeeid:
        Returns:
            bool indicating totals for the selected report is now set
        """
        filters = [("workdate", "=", "and"), ("employeeid", "=")]
        values = (workdate, employeeid)

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_CALCULATOR:
            print("\033[1;30m{} ->select_by_id\n  ->sql: {}\n  ->filters: {}\n  ->values: {}".format(
                self.model["name"], sql, filters, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CALCULATOR:
            print("  ->success: {}\n  ->data   : {}\033[0;m".format(success, data))

        if success and data:
            self._totals = dict(zip(self.model["fields"], data[0]))
            return self._totals
        return False

    def update(self):
        """
        Update totals in database if necessary

        Returns:
            bool indicating if update was a success
        """
        fields = list(self.model["fields"])[1:]
        filters = [("calcid", "=")]
        values = self.q.values_to_arg(self._totals.values())

        sql = self.q.build("update", self.model, update=fields, filteron=filters)

        if config.DEBUG_CALCULATOR:
            print("\033[1;30m{} ->select_by_id\n  ->sql: {}\n  ->fields: {}\n  ->filters: {}\n  ->values{}".format(
                self.model["name"], sql, fields, filters, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CALCULATOR:
            print("  ->success: {}\n  ->data   : {}\033[1;30m".format(success, data))

        if success and data:
            return True
        return False
