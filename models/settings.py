#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Settings class"""
import sqlite3

from configuration import config
from util import dbfn
from util.query import Query


class Setting:
    def __init__(self):
        """Initialize the Settings class"""
        self.model = {
            "name": "settings",
            "fields": ("usermail", "userpass", "usercountry", "pd", "pf", "sf",
                       "http", "smtp", "port", "mailto",
                       "mailserver", "mailport", "mailuser", "mailpass",
                       "fc", "fp", "fe", "lsc", "lsp", "sac", "sap", "sc"),
            "types": ("TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER")
        }
        self.settings = {}
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def current_settings(self):
        try:
            _ = self.settings["usermail"]
        except KeyError:
            self.load_()
        return self.settings

    @current_settings.setter
    def current_settings(self, settings):
        self.settings = settings

    def insert_(self, data):
        """Insert settings data"""
        sql = "INSERT INTO settings " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        if not type(data) == list:
            list(data)
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, data)
            db.commit()

    def insert_defaults(self):
        """Create default settings in database"""
        defaults = ["", "", "", "_", "__", ".txt",
                    "", "", "", "", "", "", "", "",
                    "customers", "invenprices", "employees", "", "", "", "", 0]
        self.insert_(defaults)  # call insert function

    def load_(self):
        """Load settings"""
        sql = "SELECT * FROM settings"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchone()
            if not data:
                self.insert_defaults()
                cur.execute(sql)
                data = cur.fetchone()
            self.settings = dict(zip(self.model["fields"], data))

    def update_(self):
        """Update settings"""
        sql = "UPDATE settings SET " \
              "usermail=?, userpass=?, usercountry=?, " \
              "pd=?, pf=?, sf=?, " \
              "http=?, smtp=?, port=?, mailto=?, " \
              "mailserver=?, mailport=?, mailuser=?, mailpass=?, " \
              "fc=?, fp=?, fe=?, lsc=?, lsp=?, sac=?, sap=?, sc=?;"
        values = list(self.settings.values())
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()
