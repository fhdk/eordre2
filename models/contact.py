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
        # model for zipping dictionary
        self.model = ("contactid", "customerid", "name", "department", "email", "phone", "infotext")
        self.__contact = {}
        self.__contacts = []

    @property
    def currentcontact(self):
        return self.__contact

    @property
    def contactlist(self):
        return self.__contacts

    @contactlist.setter
    def contactlist(self, customerid):
        try:
            _ = self.__contacts[0]
        except IndexError:
            self.__contacts = self.load_(customerid)

    def find_(self, contactid):
        sql = "SELECT * FROM contact WHERE contactid=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (contactid,))
            contact = cur.fetchone()
            if contact:
                self.__contact = dict(zip(self.model, contact))

    def insert_(self, values):
        """Insert items
        :param values: contact data to insert in contact table
        """
        sql = "INSERT INTO contact (contactid, customerid, name, department, email, phone, infotext) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.executemany(sql, (values,))
            db.commit()

    def insert_csv(self, filename, headers=False):
        """Import contact from file
        :param filename:
        :param headers:
        """
        dbfn.recreate_table("contact")
        filename.encode("utf8")
        conn = sqlite3.connect(config.DBPATH)
        with conn:
            with open(filename) as csvdata:
                reader = csv.reader(csvdata)
                line = 0
                for row in reader:
                    line += 1
                    if headers and line == 1:
                        continue
                    processed = [row[0], row[1], row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                                 row[6].strip()]
                    self.insert_(processed)

    def load_(self, customerid):
        """Load contact"""
        sql = "SELECT * FROM contact WHERE customerid=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.execute(sql, (customerid,))
            contact = cur.fetchall()
            if contact:
                return [dict(zip(self.model, row)) for row in contact]
            return []

    def update_(self, values):
        """Update item"""
        sql = "UPDATE contact SET name=?, department=?, email=?, phone=?, infotext=? WHERE contactid=?;"
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, values)
            db.commit()
