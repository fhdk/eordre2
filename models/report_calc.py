# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Report Calculation module
"""

from configuration import config
from models.query import Query


class ReportCalc:
    """
    Report Calculation
    """
    def __init__(self):
        """
        Initialize ReportCalc
        """
        self.model = {
            "name": "totals",
            "id": "totalsid",
            "fields": ("totalsid", "preworkdate", "reportid", "employeeid",
                       "new_visit", "new_demo", "new_sale", "new_turnover",
                       "recall_visit", "recall_demo", "recall_sale", "recall_turnover",
                       "sas", "sas_turnover", "visit", "demo", "sale", "turnover",
                       "kmwork", "kmprivate", "workdays", "offdays", "reports"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT NOT NULL", "INTEGER NOT NULL", "INTEGER NOT NULL",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "REAL DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "INTEGER DEFAULT 0")
        }
        self._totals = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_REPORT_CALC:
                print("{} -> table\nsuccess: {}\ndata   : {}".format(self.model["name"].upper(), success, data))

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
        # build query and execute
        sql = self.q.build("insert", self.model)
        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT_CALC:
            print("{} -> insert\nsuccess: {}\ndata   : {}".format(self.model["name"].upper(), success, data))

        if success and data:
            self.select_by_id(data)

    def select_by_id(self, totals_id):
        """
        Select by id
        Returns:
            bool indicating totals has been set for the requested id
        """
        where_list = [(self.model["id"], "=")]
        values = [totals_id]
        # build query and execute
        sql = self.q.build("select", self.model, filteron=where_list)
        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT_CALC:
            print("{} -> select_by_id\nsuccess: {}\ndata   : {}".format(self.model["name"].upper(), success, data))

        if success and data:
            self._totals = dict(zip(self.model["fields"], data[0]))
            return True
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
        where_list = [("workdate", "=", "and"), ("employeeid", "=")]
        values = [workdate, employeeid]
        # build query and execute
        sql = self.q.build("select", self.model, filteron=where_list)
        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT_CALC:
            print("{} -> select_by_id\nsuccess: {}\ndata   : {}".format(self.model["name"].upper(), success, data))

        if success and data:
            self._totals = dict(zip(self.model["fields"], data[0]))
            return True
        return False

    def update(self):
        """
        Update totals in database if necessary

        Returns:
            bool indicating if update was a success
        """
        update_list = list(self.model["fields"])[1:]
        where_list = [(self.model["id"]), "="]
        values = self.q.values_to_arg(self._totals.values())
        # build query and execute
        sql = self.q.build("update", self.model, update=update_list, filteron=where_list)
        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT_CALC:
            print("{} -> select_by_id\nsuccess: {}\ndata   : {}".format(self.model["name"].upper(), success, data))

        if success and data:
            return True
        return False
