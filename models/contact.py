#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Contact class"""

from configuration import config
import csv

from models.query import Query


class Contact:
    """
    Customer Contacts
    """

    def __init__(self):
        """Initialize Contact class"""
        self.model = {
            "name": "contact",
            "id": "contactid",
            "fields": ("contactid", "customerid", "name", "department", "email", "phone", "infotext"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT")
        }
        self._contact = {}
        self._contacts = []
        self.csv_field_count = 8
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_CONTACT:
                print(
                    "\033[1;36m{}\n ->table\n  ->success: {}\n  ->data: {}\033[1;m".format(
                        self.model["name"].upper(), success, data))

    def clear(self):
        """
        Clear internal variables
        """
        self._contact = {}
        self._contacts = []

    def create(self, customerid, name):
        """
        Create a contact
        """
        values = (None, customerid, name, "", "", "", "")
        data = self.insert(values)
        self.find(data)

    def find(self, contactid):
        """
        Load specific contact by id
        Args:
            contactid:
        """
        values = (contactid,)
        # build query and execute
        sql = self.q.build("select", self.model)
        success, data = self.q.execute(sql, values=values)
        if success and data:
            self._contact = dict(zip(self.model["fields"], data))

    def import_csv(self, filename, headers=False):
        """
        Import contact from file
        Args:
            filename: 
            headers: 
        """
        self.recreate_table()
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                if config.DEBUG_CONTACT:
                    print(
                        "\033[1;36m{}\n ->import_csv\n  ->row: {}\033[1;m".format(
                            self.model["name"].upper(), row))
                if not len(row) == self.csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # skip the
                values = (row[0], row[1], row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[7].strip())
                if config.DEBUG_CONTACT:
                    print(
                        "\033[1;36m{}\n ->import_csv\n  ->values: {}\033[1;m".format(
                            self.model["name"].upper(), values))
                self.insert(values)

            return True

    def insert(self, values):
        """
        Insert items
        Args:
            values: contact data to insert in contact table
        """
        # build query and execute
        sql = self.q.build("insert", self.model)
        if config.DEBUG_CONTACT:
            print(
                "\033[1;36m{}\n ->insert\n  ->sql: {}\n  ->values: {}\033[1;m".format(
                    self.model["name"].upper(), sql, values))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_CONTACT:
            print(
                "\033[1;36m{}\n ->insert\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))
        if success and data:
            return data
        return False

    def load_for_customer(self, customerid):
        """
        Load contacts for customer
        Args:
            customerid:
        """
        filteron = (self.model["id"], "=")
        values = (customerid,)
        # build query and execute
        sql = self.q.build("select", self.model, filteron=filteron)

        if config.DEBUG_CONTACT:
            print(
                "\033[1;36m{}\n ->select for customer\n  ->sql: {}\033[1;m".format(
                    self.model["name"].upper(), sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CONTACT:
            print(
                "\033[1;36m{}\n ->select for customer\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

        if success and data:
            self._contacts = [dict(zip(self.model["fields"], row)) for row in data]
        else:
            self._contacts = []

    def recreate_table(self):
        """
        Drop and create table
        """
        # build query and execute
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)

    def update(self):
        """
        Update item
        """
        fields = list(self.model["fields"])[1:]
        filteron = (self.model["id"], "=")
        # move id from first to last element
        values = self.q.values_to_arg(self._contact.values())
        # build query and execute
        sql = self.q.build("update", self.model, update=fields, filteron=filteron)
        self.q.execute(sql, values=values)
