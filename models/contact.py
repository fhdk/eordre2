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

            sql = self.q.build("create", self.model)

            success, data = self.q.execute(sql)

            if config.DEBUG_CONTACT:
                print("\033[1;31m\n ->table\n  ->success: {}\n  ->data: {}\033[0;m".format(
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

        return self._contact

    def find(self, contactid):
        """
        Load specific contact by id
        Args:
            contactid:
        """
        values = (contactid,)

        sql = self.q.build("select", self.model)

        if config.DEBUG_CONTACT:
            print("\033[1;31m\n ->find\n  ->values: {}\n  ->values: {}".format(
                self.model["name"].upper(), values, sql))

        success, data = self.q.execute(sql, values=values)

        if success and data:
            self._contact = dict(zip(self.model["fields"], data))

        if config.DEBUG_CONTACT:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            return self._contact

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
                    print("\033[1;31m\n ->import_csv\n  ->row: {}".format(self.model["name"].upper(), row))

                if not len(row) == self.csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue

                values = (row[0], row[1], row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[7].strip())

                if config.DEBUG_CONTACT:
                    print("  ->values: {}\033[0;m".format(values))

                self.insert(values)

            return True

    def insert(self, values):
        """
        Insert items
        Args:
            values: contact data to insert in contact table
        """

        sql = self.q.build("insert", self.model)

        if config.DEBUG_CONTACT:
            print("\033[1;31m\n ->insert\n  ->values: {}\n  ->sql: {}".format(
                self.model["name"].upper(), values, sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CONTACT:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            return data
        return False

    def load_for_customer(self, customerid):
        """
        Load contacts for customer
        Args:
            customerid:
        """
        filters = [("customerid", "=")]
        values = (customerid,)

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_CONTACT:
            print("\033[1;31m\n ->load for customer\n  ->filters: {}\n  ->values: {}\n  ->sql: {}".format(
                    self.model["name"].upper(), filters, values, sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CONTACT:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            self._contacts = [dict(zip(self.model["fields"], row)) for row in data]
        else:
            self._contacts = []
        return self._contacts

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
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._contact.values())

        sql = self.q.build("update", self.model, update=fields, filteron=filters)

        if config.DEBUG_CONTACT:
            print("\033[1;31m\n ->update\n  ->fields: {}\n  ->filters: {}\n  ->values: {}\n  ->sql: {}".format(
                self.model["name"].upper(), fields, filters, values, sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CONTACT:
            print("  ->success: {}\n  ->data: {}\033[0;m".format(success, data))

        if success and data:
            return True
        return False
