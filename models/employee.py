#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Employee Module
"""

from models.query import Query
from models.settings import Settings
from util import httpfn, rules

B_COLOR = "\033[0;34m"
E_COLOR = "\033[0;m"
DBG = False

__module__ = "employee"


def printit(string):
    """Print a variable string for debug purposes"""
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class Employee:
    """
    Employee class
    """

    def __init__(self):
        """
        Initialize Employee class
        """
        self.model = {
            "name": "employee",
            "id": "employee_id",
            "fields": ("employee_id", "salesrep", "fullname", "email", "country", "sas"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER DEFAULT 0")
        }
        self._employee = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if DBG:
                printit(" ->init_detail table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))
        self.s = Settings()
        if rules.check_settings(self.s.active):
            self.load(self.s.active["usermail"])

    @property
    def active(self):
        """
        Return current and only employeeid
        """
        return self._employee

    def insert(self, values):
        """
        Insert employee in database
        Args:
            values:
        """
        sql = self.q.build("insert", self.model)

        if DBG:
            printit(" ->insert\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(sql, values))

        success, data = self.q.execute(sql, values=values)

        if DBG:
            printit("  ->success: {}\n"
                    "  -->data: {}".format(success, data))

    def load(self, email):
        """
        Load the employee
        """
        filters = [("email", "=")]
        values = (email,)
        sql = self.q.build("select", self.model, filters=filters)

        if DBG:
            printit(" ->all\n"
                    "  ->sql: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}".format(sql, filters, values))

        success, data = self.q.execute(sql, values)
        if DBG:
            printit("  ->first check\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        try:
            _ = data[0]
            self._employee = dict(zip(self.model["fields"], data[0]))
        except IndexError:
            if httpfn.inet_conn_check():
                self.load_from_http()

                success, data = self.q.execute(sql, values)
                if DBG:
                    printit("  ->second check\n"
                            "  ->success: {}\n"
                            "  ->data: {}".format(success, data))
                try:
                    _ = data[0]
                    self._employee = dict(zip(self.model["fields"], data[0]))
                except IndexError:
                    self._employee = {}

    def load_from_http(self):
        """
        Load employee from http
        """
        data = httpfn.get_employee_data(self.s)
        if DBG:
            printit("  ->load_from_http\n"
                    "  ->data: {}".format(data))
        if data:
            data = list(data)
            data[0:0] = [None]
            self.insert(tuple(data))

    def update(self):
        """
        Update employee in database
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._employee.values())

        sql = self.q.build("update", self.model, update=fields, filters=filters)

        if DBG:
            printit(" ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(sql, fields, filters, values))

        success, data = self.q.execute(sql, values=values)

        if DBG:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
