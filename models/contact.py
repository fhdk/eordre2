#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Contact class"""
import csv
import sqlite3

from configuration import config
from util import dbfn


class Contact:
    def __init__(self):
        """Initialize Contact class"""
        self.model = {
            "name": "contact",
            "fields": ("contactid", "customerid", "name", "department", "email", "phone", "infotext"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT")
        }
        self._contact = {}
        self._contacts = []
        self.csv_field_count = 8

    @property
    def contact(self):
        return self._contact

    @property
    def contacts(self):
        return self._contacts

    @contacts.setter
    def contacts(self, customerid):
        try:
            custid = self._contacts[0]["customerid"]
            if not custid == customerid:
                self.load_for_customer(customerid)
        except IndexError:
            self.load_for_customer(customerid)

    def clear(self):
        self._contact = {}
        self._contacts = []

    def create(self, customerid, name):
        """Create a contact"""
        values = (None, customerid, name, "", "", "", "")
        self.insert(values)
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            self.find(cur.execute("SELECT last_insert_rowid();"))

    def find(self, contactid):
        sql = "SELECT * FROM contact WHERE contactid=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (contactid,))
            contact = cur.fetchone()
            if contact:
                self._contact = dict(zip(self.model["fields"], contact))

    def import_csv(self, filename, headers=False):
        """Import contact from file
        :param filename:
        :param headers:
        """
        dbfn.recreate_table("contact")
        filename.encode("utf8")
        csv_field_count = 7
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                if not len(row) == csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                values = [row[0], row[1], row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[7].strip()]
                self.insert(values)
            return True

    def insert(self, values):
        """Insert items
        :param values: contact data to insert in contact table
        """
        sql = "INSERT INTO contact VALUES (?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        # sanitize parameter
        if not type(values) == list:
            values = list(values)
        with db:
            db.execute(sql, values)
            db.commit()

    def load_for_customer(self, customerid):
        """Load contact"""
        sql = "SELECT * FROM contact WHERE customerid=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.execute(sql, (customerid,))
            contacts = cur.fetchall()
            if contacts:
                self._contacts = [dict(zip(self.model["fields"], row)) for row in contacts]
            else:
                self._contacts = []

    def update(self, values):
        """Update item"""
        sql = "UPDATE contact SET contactid=?, name=?, department=?, email=?, phone=?, infotext=? WHERE contactid=?;"
        # sanitize parameter
        if not type(values) == list:
            values = list(values)
        values += values[0]
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, list(values))
            db.commit()
