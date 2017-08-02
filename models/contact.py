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
from util.query import Query


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
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

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
        sql = self.q.build("insert", self.model)
        value_list = (None, customerid, name, "", "", "", "")
        result = self.q.execute(sql, value_list=value_list)
        self.find(result)

    def find(self, contactid):
        sql = self.q.build("select", self.model)
        value_list = list(contactid)
        result = self.q.execute(sql, value_list=value_list)
        if result:
            self._contact = dict(zip(self.model["fields"], result))

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
        value_list = []
        if not type(values) == list:
            value_list = list(values)
        sql = self.q.build("insert", self.model)
        return self.q.execute(sql, value_list=value_list)

    def load_for_customer(self, customerid):
        """Load contact"""
        where_list = list("customerid")
        sql = self.q.build("select", self.model, where_list=where_list)
        value_list = list(customerid)
        contacts = self.q.execute(sql, value_list=value_list)
        if contacts:
            self._contacts = [dict(zip(self.model["fields"], row)) for row in contacts]
        else:
            self._contacts = []

    def update(self, values):
        """Update item"""
        update_list = list(self.model["fields"])[1:]
        where_list = ["contactid"]
        sql = self.q.build("update", update_list=update_list, where_list=where_list)
        value_list = []
        # sanitize parameter
        if not type(values) == list:
            value_list = list(values)
        value_list = value_list.append(value_list[0])[1:]
        self.q.execute(sql, value_list=value_list)
