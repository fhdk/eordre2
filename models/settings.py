#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
settings module
"""

from configuration import config
from models.query import Query

B_COLOR = "\033[1;34m"
E_COLOR = "\033[0;1m"

__module__ = "settings"


def printit(string):
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class Settings:
    """
    settings class
    """

    def __init__(self):
        """
        Initialize the settings class
        """
        self.model = {
            "name": "settings",
            "id": "settings_id",
            "fields": ("settings_id", "usermail", "userpass", "usercountry", "pd", "pf", "sf",
                       "http", "smtp", "port", "mailto", "mailserver", "mailport", "mailuser", "mailpass",
                       "fc", "fp", "fe", "lsc", "lsp", "sac", "sap", "sc"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER")
        }
        self._settings = {}
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_SETTINGS:
                printit(" ->table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))

    @property
    def current(self):
        """
        current
        Returns:
            The current settings
        """
        try:
            _ = self._settings["usermail"]
        except KeyError:
            self.load()

        return self._settings

    @current.setter
    def current(self, settings):
        """
        Pushing new current settings
        Args:
            settings:
        """
        self._settings = settings
        self.update()

    def insert(self, values):
        """
        Inserts in database and activates the current settings values
        Args:
            values:

        Returns:

        """

        sql = self.q.build("insert", self.model)

        if config.DEBUG_SETTINGS:
            printit(" ->insert\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_SETTINGS:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success and data:
            self._settings = dict(zip(self.model["fields"], values))

    def load(self):
        """
        Load current
        """
        sql = self.q.build("select", self.model)

        if config.DEBUG_SETTINGS:
            printit(" ->all\n"
                    "  ->sql: {}".format(sql))

        success, data = self.q.execute(sql)

        if success and not data:
            values = (None, "", "", "", "_", "__", ".txt", "", "", "", "", "", "", "", "",
                      "customers", "invenprices", "employees", "", "", "", "", 0)

            self.insert(values)

            success, data = self.q.execute(sql)

        if success and data:
            self._settings = dict(zip(self.model["fields"], data[0]))

        if config.DEBUG_SETTINGS:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success and data:
            return data

        return False

    def update(self):
        """
        Update current
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._settings.values())

        sql = self.q.build("update", self.model, update=fields, filteron=filters)

        if config.DEBUG_SETTINGS:
            printit(" ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(fields, filters, values, sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_SETTINGS:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success and data:
            return data

        return False
