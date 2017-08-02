#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Orderhead class"""

import csv

from models.query import Query
from util import dbfn, utils


# noinspection PyMethodMayBeStatic
class Visit:
    def __init__(self):
        """Initialize visit class"""
        self.model = {
            "name": "visit",
            "id": "visitid",
            "fields": ("visitid", "reportid", "employeeid", "customerid", "podate", "posent", "pocontact", "ponum",
                       "pocompany", "poaddress1", "poaddress2", "popostcode", "popostoffice", "pocountry", "infotext",
                       "proddemo", "prodsale", "ordertype", "turnsas", "turnsale", "turntotal", "approved"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER", "INTEGER", "INTEGER", "TEXT", "INTEGER",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "REAL", "REAL", "REAL", "INTEGER")
        }
        self._customer_visits = []
        self._report_visits = []
        self._visit = {}
        self.csv_field_count = 22
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def visit(self):
        return self._visit

    @property
    def customer_visits(self):
        return self._customer_visits

    @customer_visits.setter
    def customer_visits(self, customerid):
        try:
            cid = self._customer_visits[0]["customerid"]
            if not cid == customerid:
                self.select_by_customer(customerid=customerid)
        except IndexError:
            self.select_by_customer(customerid=customerid)

    @property
    def report_visits(self):
        return self._report_visits

    @report_visits.setter
    def report_visits(self, reportid):
        try:
            rid = self._report_visits[0]["reportid"]
            if not rid == reportid:
                self.select_by_report(reportid)
        except IndexError:
            self.select_by_report(reportid=reportid)

    def clear(self):
        self._visit = {}
        self._customer_visits = []
        self._report_visits = []

    def create(self, reportid, employeeid, customerid, workdate):
        values = [None, reportid, employeeid, customerid, workdate,
                  0, "", "", "", "", "", "", "", "", "", "", "", "", 0.0, 0.0, 0.0, 0]
        self.find(self.insert(values))

    def find(self, visitid):
        """Look up a visit from visitid"""
        where_list = [(self.model["id"], "=")]
        value_list = [visitid]
        sql = self.q.build("select", self.model, where_list=where_list)
        success, data = self.q.execute(sql, value_list=value_list)
        if success and data:
            self._visit = dict(zip(self.model["fields"], data))

    def import_csv(self, filename, headers=False):
        """Import orders from file
        :param filename:
        :param headers:
        """
        self.recreate_table()
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                if not len(row) == self.csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # translate bool text to integer col 5
                row[5] = utils.bool2int(utils.str2bool(row[5]))
                processed = [row[0], row[1], row[2], row[3], row[4].strip(),
                             row[5], row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(),
                             row[10].strip(), row[11].strip(), row[12].strip(), row[13].strip(), row[14].strip(),
                             row[15].strip(), row[16].strip(), row[17].strip(), row[18], row[19],
                             row[20], row[21]]
                self.insert(processed)  # call insert function
            return True

    def insert(self, values=None):
        """Save visit"""
        sql = self.q.build("insert", self.model)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(self._visit.values())
        success, data = self.q.execute(sql, value_list=value_list)
        if success and data:
            return data

    def recreate_table(self):
        """Drop and create table"""
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)

    def select_by_customer(self, customerid):
        """Load visits for specified customer"""
        where_list = [(self.model["id"]), "="]
        value_list = [customerid]
        sql = self.q.build("select", self.model, where_list=where_list)
        success, data = self.q.execute(sql, value_list=value_list)
        if success and data:
            self._customer_visits = [dict(zip(self.model["fields"], row)) for row in data]

    def select_by_report(self, reportid):
        """Load orders for specified customer"""
        where_list = [(self.model["id"], "=")]
        value_list = [reportid]
        sql = self.q.build("select", self.model, where_list=where_list)
        success, data = self.q.execute(sql, value_list=value_list)
        if success and data:
            self._report_visits = [dict(zip(self.model["fields"], row)) for row in data]

    def save(self):
        """Save"""
        self._update_()

    def _update_(self, values=None):
        """Save current visit"""
        where_list = [(self.model["id"]), "="]
        sql = self.q.build("update", self.model, where_list=where_list)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(self._visit.values())
        rowid = value_list[0]
        value_list = value_list[1:]
        value_list.append(rowid)
        self.q.execute(sql, value_list=value_list)
