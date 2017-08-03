#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""Employee class"""

from models.query import Query
from util import dbfn


class Employee:
    def __init__(self):
        """Initialize Employee class"""
        # model for zipping dictionary
        self.model = {
            "name": "employee",
            "id": "employeeid",
            "fields": ("employeeid", "salesrep", "fullname", "email", "country", "sas"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER")
        }
        self._employee = {}
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def employee(self):
        """Return current and only employee"""
        try:
            _ = self._employee["fullname"]
        except KeyError:
            self.load()
        return self._employee

    def insert(self, values):
        """Insert employee in database"""
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            list(value_list)
        # build query and execute
        sql = self.q.build("insert", self.model)
        self.q.execute(sql, values=value_list)

    def load(self):
        """Load the employee"""
        # build query and execute
        sql = self.q.build("select", self.model)
        success, data = self.q.execute(sql)
        if success and data:
            self._employee = dict(zip(self.model["fields"], data[0]))

    def update(self):
        """Update the employee"""
        update_list = list(self.model["fields"])[1:]
        where_list = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._employee.values())
        # build query and execute
        sql = self.q.build("update", self.model, update=update_list, where=where_list)
        self.q.execute(sql, values=values)
