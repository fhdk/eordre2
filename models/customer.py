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
            "id": "customerid",
            "fields": ("customerid", "account", "company",
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
        self.csv_field_count = 20
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_CUSTOMER:
                print(
                    "\033[1;33m{}\n ->create table\n  ->success: {}\n  ->data: {}\033[1;m".format(
                        self.model["name"].upper(), success, data))

    def clear(self):
        """
        Clear internal variables
        """
        self._customer = {}
        self._customers = []

    @property
    def customer(self):
        """
        Return current customer
        """
        return self._customer

    @property
    def customers(self):
        """
        Load customer into primary customer list
        """
        try:
            _ = self._customers[0]
        except IndexError:
            self.load()
        return self._customers

    # TODO: refactor this
    def add(self, company, phone, createdate, country, salesrep):
        """
        Add a new customer
        Args:
            company:
            phone:
            createdate:
            country:
            salesrep:
        """
        # do we have the customer
        found = self.lookup_by_phone_name(phone, company)
        if found:
            self._customer = found
        else:
            # build query and execute
            sql = self.q.build("insert", self.model)
            sql = self.q.execute(sql)
            value_list = [None, "NY", company, "", "", "", "", country, salesrep,
                          phone, "", "", 0, 0, createdate, "", "", "", 0.0]
            success, data = self.q.execute(sql, value_list)
            if success and data:
                self.lookup_by_id(data)

    def lookup_by_id(self, customerid):
        """
        Find customer by id
        Args:
            customerid
        """
        filters = [(self.model["id"], "=")]
        values = (customerid,)
        # build query and execute
        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->lookup id\n  ->sql: {}\033[1;m".format(
                    self.model["name"].upper(), sql))

        success, data = self.q.execute(sql, values=values)

        if success and data:
            self._customer = dict(zip(self.model["fields"], data))

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->lookup id\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data[0]))

    def lookup_by_phone_name(self, phone, company):
        """
        Look up customer
        Args:
            phone: 
            company: 
        """
        # search by account
        filters = [("phone1", "=", "or"), ("account", "=")]
        values = (phone, phone)
        # build query and execute

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->lookup phone\n  ->sql: {}\033[1;m".format(
                    self.model["name"].upper(), sql))

        success, data = self.q.execute(sql, values=values)

        if not success:
            # retry search which "NY" as account
            filters = [("account", "=", "and"), ("company", "=", "or"), ("phone1", "=")]
            values = ("NY", company, phone)
            # build query and execute
            sql = self.q.build("select", self.model, filteron=filters)
            success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->lookup phone\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

        if success and data:
            self._customer = dict(zip(self.model["fields"], data[0]))
            return True
        return False

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
                    print(
                        "\033[1;33m{}\n ->import_csv\n  ->row: {}\033[1;m".format(
                            self.model["name"].upper(), row))
                if not len(row) == self.csv_field_count:
                    return False
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
                    print(
                        "\033[1;33m{}\n ->import_csv\n  ->values: {}\033[1;m".format(
                            self.model["name"].upper(), values))
                self.insert(values)
            return True

    def import_http(self, values):
        """
        Insert a new customer
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
        # lookup existing customer
        if self.lookup_by_phone_name(values[0], values[1]):
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
        Insert a new customer
        Args:
            values:

        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        value_list = list(values)

        # build query and execute
        sql = self.q.build("insert", self.model)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->insert\n  ->sql: {}\033[1;m".format(
                    self.model["name"].upper(), sql))

        success, data = self.q.execute(sql, values=value_list)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->insert\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

        if success and data:
            return data

    def load(self):
        """
        Load customers into primary customer list
        """
        # build query and execute
        sql = self.q.build("select", self.model)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->load\n  ->sql: {}\033[1;m".format(
                    self.model["name"].upper(), sql))

        success, data = self.q.execute(sql)

        if success and data:
            self._customers = [dict(zip(self.model["fields"], row)) for row in data]

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->load\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

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
        Update customer in database

        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        update_list = list(self.model["fields"])[1:]
        where_list = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._customer.values())
        # build query and execute
        sql = self.q.build("update", self.model, update=update_list, filteron=where_list)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->update\n  ->sql: {}\033[1;m".format(
                    self.model["name"].upper(), sql))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_CUSTOMER:
            print(
                "\033[1;33m{}\n ->update\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))
