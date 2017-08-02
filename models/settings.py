#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Settings class"""

from util import dbfn
from util.query import Query


class Setting:
    def __init__(self):
        """Initialize the Settings class"""
        self.model = {
            "name": "settings",
            "id": "settingsid",
            "fields": ("settingsid", "usermail", "userpass", "usercountry", "pd", "pf", "sf",
                       "http", "smtp", "port", "mailto", "mailserver", "mailport", "mailuser", "mailpass",
                       "fc", "fp", "fe", "lsc", "lsp", "sac", "sap", "sc"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER")
        }
        self._settings = {}
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def settings(self):
        try:
            _ = self._settings["usermail"]
        except KeyError:
            self.load()
        return self._settings

    @settings.setter
    def settings(self, settings):
        self._settings = settings

    def insert(self, values):
        """Insert settings data"""
        sql = self.q.build("insert", self.model)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        value_list = value_list.append(value_list[0])[1:]
        self.q.execute(sql, value_list=value_list)

    def insert_defaults(self):
        """Create default settings in database"""
        defaults = ["", "", "", "_", "__", ".txt",
                    "", "", "", "", "", "", "", "",
                    "customers", "invenprices", "employees", "", "", "", "", 0]
        self.insert(defaults)  # call insert function

    def load(self):
        """Load settings"""
        sql = self.q.build("select", self.model)
        result = self.q.execute(sql)
        if not result:
            self.insert_defaults()
            result = self.q.execute(sql)
        self._settings = dict(zip(self.model["fields"], result))

    def update(self):
        """Update settings"""
        where_list = [(self.model["id"], "=")]
        value_list = list(self._settings.values())
        sql = self.q.build("update", self.model, where_list=where_list)
        value_list = value_list.append(value_list[0])[1:]
        self.q.execute(sql, value_list=value_list)
