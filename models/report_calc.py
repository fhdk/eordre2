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
            "name": "temptotals",
            "fields": ("workdate", "reportid", "employeeid",
                       "new_visit", "new_demo", "new_sale", "new_turnover",
                       "recall_visit", "recall_demo", "recall_sale", "recall_turnover",
                       "sas", "sas_turnover", "visit", "demo", "sale", "turnover",
                       "kmwork", "kmprivate", "workdays", "offdays", "reports"),
            "types": ("TEXT", "INTEGER", "INTEGER",
                      "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "REAL", "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER")
        }
        self.totals = {}
        self.query = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.query.build("table", self.model)
            self.query.execute(sql)

    def current_totals(self):
        return self.totals

    def save_totals(self):
        pass

    def get_totals(self, workdate, employeeid):
        pass
