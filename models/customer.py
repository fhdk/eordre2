#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""CustomerNg class"""
import csv

from configuration import config
from models.query import Query
from util import utils

B_COLOR = "\033[0;33m"
E_COLOR = "\033[0;m"


def printit(string):
    print("{}{}{}".format(B_COLOR, string, E_COLOR))


class Customer:
    """
    Customer
    """

    def __init__(self):
        """
        Initialize Customer class
        """
        self.model = {
            "name": "customer",
            "id": "customer_id",
            "fields": ("customer_id", "account", "company",
                       "address1", "address2", "zipcode", "city", "country",
                       "salesrep", "phone1", "vat", "email", "deleted", "modified",
                       "created", "infotext", "att", "phone2", "factor",
                       "body", "plate", "paint", "industry"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT NOT NULL", "TEXT", "TEXT", "TEXT", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "TEXT", "TEXT", "TEXT", "TEXT", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0")
        }
        self._customers = []
        self._customer = {}
        self._csv_field_count = 20
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_CUSTOMER:
                printit("{}\n"
                        " ->create table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(self.model["name"], success, data))

    @property
    def current(self):
        """
        Return current current
        """
        return self._customer

    @current.setter
    def current(self, look_for):
        """
        Set customer based on look_for
        Args:
            look_for: str
        """
        try:
            cp = look_for[1]
            ph = look_for[0]
            try:
                name = self._customer["company"]
                if not name == cp:
                    self.lookup_by_phone_company(ph, cp)
            except KeyError:
                self.lookup_by_phone_company(ph, cp)
        except IndexError:
            self.lookup_by_id(look_for)

    @property
    def customers(self):
        """
        Load current into primary current list
        """
        try:
            _ = self._customers[0]
        except IndexError:
            self.load()
        return self._customers

    def clear(self):
        """
        Clear internal variables
        """
        self._customer = {}
        self._customers = []

    def create(self, phone, company, createdate, country, salesrep):
        """
        Create a new current
        Args:
            phone:
            company:
            createdate:
            country:
            salesrep:
        """
        found = self.lookup_by_phone_company(phone, company)

        if found:
            self._customer = found
            return False
        else:
            values = [None, "NY", company, "", "", "", "", country, salesrep,
                      phone, "", "", 0, 0, createdate, "", "", "", 0.0]

            new_id = self.insert(values)

            self.lookup_by_id(new_id)
        return True

    def import_csv(self, filename, headers=False):
        """
        Import customers from csv file
        Args:
            filename: 
            headers:

        The expected file format contains data in the following sequence
        in : id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info
        """
        self.recreate_table()
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter="|")
            line = 0
            for row in reader:
                if config.DEBUG_CUSTOMER:
                    printit("{}\n"
                            " ->row length {}\n"
                            "  ->row: {}".format(self.model["name"], len(row), row))
                #
                # if not len(row) == self._csv_field_count:
                #     return False

                line += 1
                if headers and line == 1:
                    continue
                # translate bool text in col 15
                row[15] = utils.bool2int(utils.str2bool(row[15]))
                values = (row[0],
                          row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(), row[10].strip(),
                          row[12].strip(), row[15], row[16], row[17],
                          row[19].strip(), "", "", 0.0, 0, 0, 0, 0)
                if config.DEBUG_CUSTOMER:
                    printit("  ->values: {}".format(values))
                self.insert(values)
            return True

    def import_http(self, values):
        """
        Insert a new current
        Args:
            values: List with values from http request

        expected incoming fields: acc comp add1 add2 zipcity country s_rep phone1 vat email att phon2
        """
        # import file has 'zip  city'
        # app use 'zip' 'city' in different columns
        # zip city can contain more than one space
        # eg '2200  København K' or '4430 Kirke Hyllinge'
        # it is necessary to find the first occurence of space
        # and insert '|' and use it to split zip and city
        loc = values[4].find(" ")
        zipcity = values[4][:loc] + "|" + values[4][loc:]
        zipcity = zipcity.split("|")
        zipcode = zipcity[0].strip()
        city = zipcity[1].strip()
        # lookup existing current
        if self.lookup_by_phone_company(values[0], values[1]):
            # sanitize and assign values
            if self._customer["account"] == 'NY':
                self._customer["account"] = values[0]
            if self._customer["modified"] == 1:
                self._customer["modified"] = 0
            self._customer["company"] = values[1].strip()
            self._customer["address1"] = values[2].strip()
            self._customer["address2"] = values[3].strip()
            self._customer["zipcode"] = zipcode  # zipcity[4]
            self._customer["city"] = city  # zipcity[4]
            # skip over country[5] and salesrep[6]
            self._customer["phone1"] = values[7].strip()
            self._customer["vat"] = values[8].strip()
            self._customer["email"] = values[9].strip()
            self._customer["att"] = values[10].strip()
            self._customer["phone2"] = values[11].strip()
            self.update()  # call update function
        else:
            row_values = (None, values[0].strip(), values[1].strip(), values[2], values[3].strip(), zipcode, city,
                          values[5].strip(), values[6].strip(), values[7].strip(), values[8].strip(),
                          values[9].strip(), 0, 0, 0, "", values[10].strip(), values[11].strip(), 0.0, 0, 0, 0, 0)
            self.insert(row_values)

    def insert(self, values):
        """
        Insert a new current
        Args:
            values:

        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """

        sql = self.q.build("insert", self.model)

        if config.DEBUG_CUSTOMER:
            printit("{}\n"
                    " ->insert\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(self.model["name"], str(values), sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CUSTOMER:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))

        if success and data:
            return data
        return False

    def load(self):
        """
        Load customers into primary current list
        """
        # build query and execute
        sql = self.q.build("select", self.model)

        if config.DEBUG_CUSTOMER:
            printit("{}\n"
                    " ->load\n"
                    "  ->sql: {}".format(self.model["name"], sql))

        success, data = self.q.execute(sql)

        if success and data:
            self._customers = [dict(zip(self.model["fields"], row)) for row in data]

        if config.DEBUG_CUSTOMER:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))
            return True
        return False

    def lookup_by_id(self, customer_id):
        """
        Find current by id
        Args:
            customer_id
        """
        filters = [("customer_id", "=")]
        values = (customer_id,)

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_CUSTOMER:
            printit("{}\n"
                    " ->lookup_by_id\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(self.model["name"], filters, str(values), sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CUSTOMER:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data[0]))

        if success and data:
            self._customer = dict(zip(self.model["fields"], data))
        return False

    def lookup_by_phone_company(self, phone, company):
        """
        Look up current
        Args:
            phone:
            company:
        """
        filters = [("phone1", "=", "or"), ("company", "=")]
        values = (phone, company)

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_CUSTOMER:
            printit("{}\n"
                    " ->lookup_by_phone_company\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(self.model["name"], filters, str(values), sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CUSTOMER:
            printit("  ->{}\n  ->success: {}\n  ->data: {}".format(self.model["name"], success, data))

        if not success:

            filters = [("account", "=", "and"), ("company", "=", "or"), ("phone1", "=")]
            values = ("NY", company, phone)

            sql = self.q.build("select", self.model, filteron=filters)

            if config.DEBUG_CUSTOMER:
                printit("   ->{}\n"
                        "   ->filters: {}\n"
                        "   ->values: {}\n"
                        "   ->sql: {}".format(self.model["name"], filters, str(values), sql))

            success, data = self.q.execute(sql, values=values)

            if config.DEBUG_CUSTOMER:
                printit("   ->{}\n"
                        "   ->success: {}\n"
                        "   ->data: {}".format(self.model["name"], success, data))

        if success and data:
            self._customer = dict(zip(self.model["fields"], data[0]))
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
        Update current in database

        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._customer.values())

        sql = self.q.build("update", self.model, update=fields, filteron=filters)

        if config.DEBUG_CUSTOMER:
            printit("{}\n"
                    " ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(self.model["name"], fields, filters, str(values), sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CUSTOMER:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))
