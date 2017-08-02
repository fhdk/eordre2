#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""CustomerNg class"""
import csv

from models.query import Query
from util import dbfn, utils


class Customer:
    def __init__(self):
        """Initialize Customer class"""
        self.model = {
            "name": "customer",
            "id": "customerid",
            "fields": ("customerid", "account", "company", "address1", "address2", "zipcode", "city", "country",
                       "salesrep", "phone1", "vat", "email", "deleted", "modified", "created", "infotext", "att",
                       "phone2", "factor"),
            "types": ("INTEGER PRIMARY KEY NOT NUL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER", "INTEGER", "TEXT", "TEXT", "TEXT", "TEXT", "REAL")
        }
        self._customers = []
        self._customer = {}
        self.csv_field_count = 20
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("add", self.model)
            self.q.execute(sql)

    def clear(self):
        self._customer = {}
        self._customers = []

    @property
    def customer(self):
        """Return current customer"""
        return self._customer

    @property
    def customers(self):
        """Load customer into primary customer list"""
        try:
            _ = self._customers[0]
        except IndexError:
            self.load()
        return self._customers

    def add(self, company, phone, createdate, country, salesrep):
        # do we have the customer
        found = self.lookup_by_phone_name(phone, company)
        if found:
            self._customer = found
        else:
            sql = self.q.build("insert", self.model)
            sql = self.q.execute(sql)
            value_list = [None, "NY", company, "", "", "", "", country, salesrep,
                          phone, "", "", 0, 0, createdate, "", "", "", 0.0]
            result = self.q.execute(sql, value_list)
            self.lookup_by_id(result)

    def lookup_by_id(self, customerid):
        """Find customer by id"""
        where_list = [(self.model["id"], "=")]
        sql = self.q.build("select", self.model, where_list=where_list)
        value_list = list(customerid)
        result = self.q.execute(sql, value_list=value_list)
        if result:
            self._customer = dict(zip(self.model["fields"], result))

    def lookup_by_phone_name(self, phone, company):
        """Look up customer
        :param phone:
        :param company:
        """
        # search by account
        where_list = [("phone", "=", "or"), ("account", "=")]
        sql = self.q.build("select", self.model, where_list=where_list)
        value_list = [phone, phone]
        result = self.q.execute(sql, value_list=value_list)

        if not result:
            where_list = [("account", "=", "and"), ("company", "=", "or"), ("phone", "=")]
            sql = self.q.build("select", self.model, where_list=where_list)
            value_list = ["NY", company, phone]
            result = self.q.execute(sql, value_list=value_list)

        self._customer = dict(zip(self.model["fields"], result))
        return self._customer

    def import_csv(self, filename, headers=False):
        """Import customer from csv file
        :param filename:
        :param headers:
        The expected file format contains data in the following sequence
        in : id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info
        """
        self.recreate_table()
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter="|")
            line = 0
            for row in reader:
                if not len(row) == self.csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # translate bool text in col 15
                row[15] = utils.bool2int(utils.str2bool(row[15]))
                values = [row[0],
                          row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(), row[10].strip(),
                          row[12].strip(), row[15], row[16], row[17],
                          row[19].strip(), "", "", 0.0]
                self.insert(values)
            return True

    def import_http(self, values):
        """Insert a new customer
        :param values: List with values from http request
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
        found = self.lookup_by_phone_name(values[0], values[1])
        if found:  # this is a complet customer with all fields
            # sanitize and assign values
            if found["account"] == 'NY':
                found["account"] = values[0]
            if found["modified"] == 1:
                found["modified"] = 0
            found["company"] = values[1].strip()
            found["address1"] = values[2].strip()
            found["address2"] = values[3].strip()
            found["zipcode"] = zipcode  # zipcity[4]
            found["city"] = city  # zipcity[4]
            # skip over country[5] and salesrep[6]
            found["phone1"] = values[7].strip()
            found["vat"] = values[8].strip()
            found["email"] = values[9].strip()
            found["att"] = values[10].strip()
            found["phone2"] = values[11].strip()
            self.update(found.values())  # call update function
        else:
            row_values = [None, values[0].strip(), values[1].strip(), values[2], values[3].strip(), zipcode, city,
                          values[5].strip(), values[6].strip(), values[7].strip(), values[8].strip(),
                          values[9].strip(), 0, 0, 0, "", values[10].strip(), values[11].strip(), 0.0]
            self.insert(row_values)

    def insert(self, values):
        """Insert a new customer
        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        sql = self.q.build("insert", self.model)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        return self.q.execute(sql, value_list=value_list)

    def load(self):
        """Load customers into primary customer list"""
        sql = self.q.build("select", self.model)
        result = self.q.execute(sql)
        self._customers = [dict(zip(self.model["fields"], row)) for row in result]

    def recreate_table(self):
        """Drop and create table"""
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)

    def save(self):
        """Save current customer changes"""
        self.update(list(self._customer.values()))

    def update(self, values):
        """Update current row
        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        where_list = [(self.model["id"], "=")]
        sql = self.q.build("update", self.model, where_list=where_list)
        value_list = values
        try:
            _ = value_list[0]
        except IndexError:
            value_list = list(values)
        value_list = value_list.append(value_list[0])[1:]
        self.q.execute(sql, value_list=value_list)
