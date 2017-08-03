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


class Employee:
    """
    Employee class
    """

    def __init__(self):
        """
        Initialize Employee class
        """
        # model for zipping dictionary
        self.model = {
            "name": "employee",
            "id": "employeeid",
            "fields": ("employeeid", "salesrep", "fullname", "email", "country", "sas"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER")
        }
        self._employee = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_EMPLOYEE:
                print("{} -> table\nsuccess: {}\ndata : {}".format(self.model["name"].upper(), success, data))
        self.s = Settings()
        if rules.check_settings(self.s.settings) and httpfn.inet_conn_check():
            self.load()
            if not self._employee:
                data = httpfn.get_employee_data(self.s.settings)
                if data:
                    print(data)
                    # e = [1] + e
                    # self.insert(e)

    @property
    def employee(self):
        """
        Return current and only employee
        """
        return self._employee

    def insert(self, values):
        """
        Insert employee in database
        Args:
            values:
        """
        # build query and execute
        sql = self.q.build("insert", self.model)

        if config.DEBUG_EMPLOYEE:
            print("{} -> insert\nsql: {}\nvalues: {}".format(self.model["name"].upper(), sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_EMPLOYEE:
            print("{} -> insert\nsuccess: {}\ndata: {}".format(self.model["name"].upper(), success, data))

    def load(self):
        """
        Load the employee
        """
        sql = self.q.build("select", self.model)

        if config.DEBUG_EMPLOYEE:
            print("{} -> load\nsql: {}".format(self.model["name"].upper(), sql))

        success, data = self.q.execute(sql)

        if success and data:
            self._employee = dict(zip(self.model["fields"], data[0]))

        if config.DEBUG_EMPLOYEE:
            print("{} -> load\nsuccess: {}\ndata: {}".format(self.model["name"].upper(), success, data))

    def update(self):
        """
        Update employee in database
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._employee.values())
        # build query and execute
        sql = self.q.build("update", self.model, update=fields, filteron=filters)

        if config.DEBUG_EMPLOYEE:
            print("{} -> update\nfields: {}\nfilters: {}\nvalues: {}\nsql: {}".format(
                self.model["name"].upper(), sql, fields, filters, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_EMPLOYEE:
            print("{} -> update\nsuccess: {}\ndata: {}".format(self.model["name"].upper(), success, data))
