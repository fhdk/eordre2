# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from util.query import Query
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
            sql = self.q.build("table", self.model)
            self.q.execute(sql)

    @property
    def totals(self):
        return self._totals

    @totals.setter
    def totals(self, values):
        try:
            if values[1] == self._totals["workdate"]:
                self._totals = dict(zip(self.model["fields"], values))
                self.update(values)
            else:
                self.insert(values)
        except KeyError:
            self.insert(values)

    def insert(self, values):
        """Save values to database"""
        sql = self.q.build("insert", self.model)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        result = self.q.execute(sql, value_list=value_list)
        self.select_by_id(result)

    def select_by_id(self, totals_id):
        """Select by id"""
        where_list = [(self.model["id"], "=")]
        sql = self.q.build("select", self.model, where_list=where_list)
        value_list = [totals_id]
        result = self.q.execute(sql, value_list=value_list)
        if result:
            self._totals = dict(zip(self.model["fields"], result))

    def select_by_employee_date(self, employeeid, workdate):
        """Select by employeeid and workdate"""
        where_list = [("workdate", "=", "and"), ("employeeid", "=")]
        sql = self.q.build("select", self.model, where_list=where_list)
        value_list = [workdate, employeeid]
        result = self.q.execute(sql, value_list=value_list)
        if result:
            self._totals = dict(zip(self.model["fields"], result))

    def update(self, values):
        """Update totals"""
        where_list = [(self.model["id"]), "="]
        sql = self.q.build("update", self.model, where_list=where_list)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        value_list = value_list.append(value_list[0])[1:]
        self.q.execute(sql, value_list=value_list)
