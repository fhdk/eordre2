#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Settings class"""

from models.query import Query
from util import dbfn


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
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        # build query and execute
        sql = self.q.build("insert", self.model)
        self.q.execute(sql, values=value_list)

    def insert_defaults(self):
        """Create default settings in database"""
        defaults = [(None, "", "", "", "_", "__", ".txt", "", "", "", "", "", "", "", "",
                    "customers", "invenprices", "employees", "", "", "", "", 0)]
        self.insert(defaults)  # call insert function

    def load(self):
        """Load settings"""
        # build query and execute
        sql = self.q.build("select", self.model)
        success, data = self.q.execute(sql)
        if success and not data:
            # insert defaults and retry
            self.insert_defaults()
            # build query and execute
            sql = self.q.build("select", self.model)
            success, data = self.q.execute(sql)
        if success and data:
            self._settings = dict(zip(self.model["fields"], data[0]))

    def update(self):
        """Update settings"""
        update_list = list(self.model["fields"])
        where_list = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._settings.values())
        # use query to update
        sql = self.q.build("update", self.model, update=update_list, where=where_list)
        self.q.execute(sql, values=values)
