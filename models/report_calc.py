# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from models.query import Query
from util import dbfn


class ReportCalc:
    def __init__(self):
        self.model = {
            "name": "totals",
            "id": "totalsid",
            "fields": ("totalsid", "workdate", "reportid", "employeeid",
                       "new_visit", "new_demo", "new_sale", "new_turnover",
                       "recall_visit", "recall_demo", "recall_sale", "recall_turnover",
                       "sas", "sas_turnover", "visit", "demo", "sale", "turnover",
                       "kmwork", "kmprivate", "workdays", "offdays", "reports"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "INTEGER", "INTEGER",
                      "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "REAL", "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER")
        }
        self._totals = {}
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def totals(self):
        return self._totals

    def seed(self, aggregate_list):
        pass

    def insert(self, values):
        """Save values to database"""
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        # build query and execute
        sql = self.q.build("insert", self.model)
        success, data = self.q.execute(sql, values=value_list)
        if success:
            self.select_by_id(data)

    def select_by_id(self, totals_id):
        """Select by id"""
        where_list = [(self.model["id"], "=")]
        value_list = [totals_id]
        # build query and execute
        sql = self.q.build("select", self.model, where=where_list)
        success, data = self.q.execute(sql, values=value_list)
        if success:
            self._totals = dict(zip(self.model["fields"], data))

    def select_by_employee_date(self, employeeid, workdate):
        """Select by employeeid and workdate"""
        where_list = [("workdate", "=", "and"), ("employeeid", "=")]
        value_list = [workdate, employeeid]
        # build query and execute
        sql = self.q.build("select", self.model, where=where_list)
        success, data = self.q.execute(sql, values=value_list)
        if success:
            self._totals = dict(zip(self.model["fields"], data))

    def update(self):
        """Update totals"""
        where_list = [(self.model["id"]), "="]
        values = self.q.values_to_arg(self._totals.values())
        # build query and execute
        sql = self.q.build("update", self.model, where=where_list)
        self.q.execute(sql, values=values)
