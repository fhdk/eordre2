#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Contact module"""

from configuration import config
import csv

from models.query import Query

__module__ = "contact"

B_COLOR = "\033[0;32m"
E_COLOR = "\033[0;m"


def printit(string):
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class Contact:
    """
    Contact class
    """
    def __init__(self):
        """Initialize contact class"""
        self.model = {
            "name": "contact",
            "id": "contact_id",
            "fields": ("contact_id", "customer_id", "name", "department", "email", "phone", "infotext"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT")
        }
        self._contact = {}
        self._contacts = []
        self._csv_field_count = 8
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_CONTACT:
                printit(" ->table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))

    @property
    def current(self):
        """
        Current contact
        :return:
        """
        return self._contact

    @current.setter
    def current(self, contact_id):
        """
        Set contact
        :return:
        """
        try:
            cid = self._contact["contact_id"][0]
            if not cid == contact_id:
                self.find(contact_id)
        except (KeyError, IndexError):
            self.find(contact_id)

    @property
    def contact_list(self):
        return self._contacts

    @contact_list.setter
    def contact_list(self, customer_id):
        try:
            cust_id = self.contact_list[0]["customer_id"]
            if not cust_id == customer_id:
                self.load_for_customer(customer_id=customer_id)
        except (IndexError, KeyError):
            self.load_for_customer(customer_id=customer_id)

    def clear(self):
        """
        Clear internal variables
        """
        self._contact = {}
        self._contacts = []

    def add(self, customer_id, name, dep=None, phone=None, email=None, info=None):
        """
        Create a contact
        """
        values = (None, customer_id, name, dep, email, phone, info)
        data = self.insert(values)
        return self.find(data)

    def delete(self, contact_id):
        """
        Delete contact
        Args:
            contact_id:
        Returns:
            bool
        """
        filters = [("contact_id", "=")]
        values = (contact_id,)
        sql = self.q.build("delete", self.model, filteron=filters)
        if config.DEBUG_CONTACT:
            printit(" ->delete\n"
                    "  ->filters: {}"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_CONTACT:
            printit("  ->{]\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return True
        return False

    def find(self, contact_id):
        """
        Load specific contact by id
        Args:
            contact_id:
        Returns:
            bool
        """
        values = (contact_id,)
        sql = self.q.build("select", self.model)
        if config.DEBUG_CONTACT:
            printit(" ->find\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(values, sql))
        success, data = self.q.execute(sql, values=values)
        if success:
            try:
                self._contact = dict(zip(self.model["fields"], data[0]))
            except IndexError:
                pass
        if config.DEBUG_CONTACT:
            printit("  ->{]\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return True
        return False

    def import_csv(self, filename, headers=False):
        """
        Import contact from file
        Args:
            filename: 
            headers:
        Returns:
            bool
        """
        self.recreate_table()
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                if config.DEBUG_CONTACT:
                    printit(" ->import_csv\n"
                            "  ->row: {}".format(row))
                if not len(row) == self._csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                values = (row[0], row[1], row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[7].strip())
                if config.DEBUG_CONTACT:
                    printit("  ->values: {}".format(values))
                self.insert(values)
            return True

    def insert(self, values):
        """
        Insert items
        Args:
            values: contact data to insert in contact table
        Returns:
            the new rowid
        """
        sql = self.q.build("insert", self.model)
        if config.DEBUG_CONTACT:
            printit(" ->insert\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_CONTACT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return data
        return False

    def load_for_customer(self, customer_id):
        """
        Load contacts for current
        Args:
            customer_id:
        Returns:
            bool
        """
        filters = [("customer_id", "=")]
        values = (customer_id,)
        sql = self.q.build("select", self.model, filteron=filters)
        if config.DEBUG_CONTACT:
            printit(" ->all for current\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_CONTACT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success:
            try:
                self._contacts = [dict(zip(self.model["fields"], row)) for row in data]
                return True
            except IndexError:
                self._contacts = []
        return False

    def recreate_table(self):
        """
        Drop and create table
        """
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
        self.clear()

    def update(self):
        """
        Update item
        Returns:
            bool
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._contact.values())
        sql = self.q.build("update", self.model, update=fields, filteron=filters)
        if config.DEBUG_CONTACT:
            printit(" ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(fields, filters, values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_CONTACT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return True
        return False
