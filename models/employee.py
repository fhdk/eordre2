#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""Employee class"""

from util import dbfn
from util.query import Query


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
        sql = self.q.build("insert", self.model)
        value_list = values
        if not type(value_list) == list:
            list(value_list)
        self.q.execute(sql, value_list=value_list)

    def load(self):
        """Load the employee"""
        sql = self.q.build("select", self.model)
        result = self.q.execute(sql)
        if result:
            self._employee = dict(zip(self.model["fields"], result))

    def update(self, values=None):
        """Update the employee"""
        update_list = list(self.model["fields"])[1:]
        value_list = list(values)
        where_list = [(self.model["id"], "=")]
        sql = self.q.build("update", self.model, update_list=update_list, where_list=where_list)
        if not values:
            value_list = list(self._employee.values())
        value_list = value_list.append(value_list[0])[1:]
        self.q.execute(sql, value_list=value_list)
