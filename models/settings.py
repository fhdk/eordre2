#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Settings class"""
import sqlite3

from configuration import config


class Setting:
    def __init__(self):
        """Initialize the Settings class"""
        # model for zipping dictionary
        self.model = (
            "usermail", "userpass", "usercountry", "pd", "pf", "sf",
            "http", "smtp", "port", "mailto", "mailserver", "mailport", "mailuser", "mailpass",
            "fc", "fp", "fe", "lsc", "lsp", "sac", "sap")

        self.__settings = {}

    @property
    def current_settings(self):
        try:
            _ = self.__settings["usermail"]
        except KeyError:
            self.load_()
        return self.__settings

    @current_settings.setter
    def current_settings(self, settings):
        self.__settings = settings

    def insert_(self, data):
        """Insert settings data"""
        sql = "INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, data)
            db.commit()

    def insert_defaults(self):
        """Create default settings in database"""
        defaults = ["", "", "", "_", "__", ".txt",
                    "", "", "", "", "", "", "", "",
                    "customers", "invenprices", "employees", "", "", "", ""]
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
            self.__settings = dict(zip(self.model, data))

    def update_(self):
        """Update settings"""
        sql = "UPDATE settings SET usermail=?, userpass=?, usercountry=?, pd=?, pf=?, sf=?, " \
              "http=?, smtp=?, port=?, mailto=?, mailserver=?, mailport=?, mailuser=?, mailpass=?, " \
              "fc=?, fp=?, fe=?, lsc=?, lsp=?, sac=?, sap=?;"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, list(self.__settings.values()))
            db.commit()

    def update_dates(self, data):
        sql = "UPDATE settings SET sac=?, sap=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (data[0], data[1]))
            db.commit()

    def update_sync(self, data):
        sql = "UPDATE settings SET lsc=?, lsp=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (data[0], data[1]))
            db.commit()
