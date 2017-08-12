#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Employee Module
"""

from configuration import config
from models.query import Query
from models.settings import Settings
from util import httpfn, rules

B_COLOR = "\033[0;34m"
E_COLOR = "\033[0;m"

__module__ = "employee"


def printit(string):
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
            if config.DEBUG_EMPLOYEE:
                printit(" ->init_detail table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))
        self.s = Settings()
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

        if config.DEBUG_EMPLOYEE:
            printit(" ->insert\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_EMPLOYEE:
            printit("  ->success: {}\n"
                    "  -->data: {}".format(success, data))

    def load(self, email):
        """
        Load the employee
        """
        filters = [("email", "=")]
        values = (email,)
        sql = self.q.build("select", self.model, filters=filters)

        if config.DEBUG_EMPLOYEE:
            printit(" ->all\n"
                    "  ->sql: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}".format(sql, filters, values))

        success, data = self.q.execute(sql, values)
        if config.DEBUG_EMPLOYEE:
            printit("  ->first check\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        try:
            _ = data[0]
            self._employee = dict(zip(self.model["fields"], data[0]))
        except IndexError:
            self.load_from_http()

            success, data = self.q.execute(sql, values)
            if config.DEBUG_EMPLOYEE:
                printit("  ->second check\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))
            try:
                _ = data[0]
                self._employee = dict(zip(self.model["fields"], data[0]))
            except IndexError:
                pass

    def load_from_http(self):
        data = httpfn.get_employee_data(self.s)
        if config.DEBUG_EMPLOYEE:
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

        if config.DEBUG_EMPLOYEE:
            printit(" ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(sql, fields, filters, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_EMPLOYEE:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
