#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
current Module
"""

from configuration import config
from models.query import Query
from models.settings import Settings
from util import httpfn, rules

B_COLOR = "\033[0;34m"
E_COLOR = "\033[0;m"


def printit(string):
    print("{}{}{}".format(B_COLOR, string, E_COLOR))


class Employee:
    """
    current class
    """

    def __init__(self):
        """
        Initialize current class
        """
        # model for zipping dictionary
        self.model = {
            "name": "employeeid",
            "id": "employeeid",
            "fields": ("employeeid", "salesrep", "fullname", "email", "country", "sas"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER DEFAULT 0")
        }
        self._employee = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_EMPLOYEE:
                printit("{}\n"
                        " ->create table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(self.model["name"], success, data))
        self.s = Settings()
        if rules.check_settings(self.s.current) and httpfn.inet_conn_check():
            self.load()
            if not self._employee:
                data = httpfn.get_employee_data(self.s.current)
                if data:
                    data = list(data)
                    data[0:0] = [None]
                    self.insert(tuple(data))

    @property
    def current(self):
        """
        Return current and only employeeid
        """
        return self._employee

    def insert(self, values):
        """
        Insert employeeid in database
        Args:
            values:
        """
        # build query and execute
        sql = self.q.build("insert", self.model)

        if config.DEBUG_EMPLOYEE:
            printit("{}\n"
                    " ->insert\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(self.model["name"], sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_EMPLOYEE:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  -->data: {}".format(self.model["name"], success, data))

    def load(self):
        """
        Load the employeeid
        """
        sql = self.q.build("select", self.model)

        if config.DEBUG_EMPLOYEE:
            printit("{}\n"
                    " ->load\n"
                    "  ->sql: {}".format(self.model["name"], sql))

        success, data = self.q.execute(sql)

        if success and data:
            self._employee = dict(zip(self.model["fields"], data[0]))

        if config.DEBUG_EMPLOYEE:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))

    def update(self):
        """
        Update employeeid in database
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._employee.values())

        sql = self.q.build("update", self.model, update=fields, filteron=filters)

        if config.DEBUG_EMPLOYEE:
            printit("{}\n"
                    " ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(self.model["name"], sql, fields, filters, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_EMPLOYEE:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))
