#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

""""Employee class"""
import sqlite3

from configuration import config


class Employee:
    # last_mod -> _employees.txt
    # sample content: 2017-06-22 09:15:30
    # __employees.txt
    def __init__(self):
        """Initialize Employee class"""
        # model for zipping dictionary
        self.model = {
            "name": "employee",
            "fields": ("employeeid", "salesrep", "fullname", "email", "country", "sas"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER")
        }
        self.employee = {}

    @property
    def current_employee(self):
        """Return current and only employee"""
        try:
            _ = self.employee["fullname"]
        except KeyError:
            self.load_()
        return self.employee

    def insert_(self, values):
        """Insert employee in database"""
        sql = "INSERT INTO employee VALUES (?, ?, ?, ?, ?, ?)"
        db = sqlite3.connect(config.DBPATH)
        if not type(values) == list:
            list(values)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()

    def load_(self):
        """Load the employee"""
        sql = "SELECT * FROM employee"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql)
            row = cur.fetchone()
            if row:
                self.employee = dict(zip(self.model["fields"], row))

    def update_(self, values=None):
        """Update the employee"""
        sql = "UPDATE employee " \
              "SET employeeid=?, salesrep=?, fullname=?, email=?, country=?, sas=? " \
              "WHERE employeeid=?;"
        if not values:
            values = list(self.employee.values())
        if not type(values) == list:
            values = list(values)
        values.append(self.employee["employeeid"])
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()
