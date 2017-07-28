#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# -----------------------------------------------------------------------------------------------
# Possible formats for data
# row: |0  |1   |2   |3   |4      |5      |6    |7      |8    |9    |10 |11   |12 |13 |14 |15  |16 |17   |19
# old:  acc comp add1 add2 zipcity country s_rep phone1  vat
# new:  acc comp add1 add2 zipcity country s_rep phone1  vat   email att phon2
# csv:  id  acc  comp add1 add2    zipcode city  country s_rep phon1 vat email del mod cre info
# db :  id  acc  comp add1 add2    zipcode city  country s_rep phon1 vat email del mod cre info att phon2 factor
# -----------------------------------------------------------------------------------------------


"""CustomerNg class"""
import csv
import sqlite3

from configuration import config
from util import dbfn


class Customer:
    # last_mod -> _customers.txt
    # sample content: 2017-06-22 09:15:30
    # __customer.txt
    def __init__(self):
        """Initialize Customer class"""
        # model for zipping dictionary
        self.model = ("customerid",
                      "account", "company", "address1", "address2", "zipcode", "city", "country",
                      "salesrep", "phone1", "vat", "email",
                      "deleted", "modified", "created",
                      "infotext", "att", "phone2", "factor")

        self.__customer_list = []
        self.__customer = {}

    @property
    def current_customer(self):
        """Return current customer"""
        return self.__customer

    @property
    def customer_list(self):
        """Load customer into primary customer list"""
        try:
            _ = self.__customer_list[0]
        except IndexError:
            self.load_()
        return self.__customer_list

    def create_(self, company, phone, createdate, country, salesrep):
        found = self.find_(phone, company)
        if found:
            self.__customer = found
        else:
            new = (None, "NY", company, "", "", "", "", country,
                   salesrep, phone, "", "", 0, 0, createdate, "", "", "", 0.0)
            self.__customer = dict(zip(self.model, new))

    def find_(self, account, company):
        """Look up customer
        :param account:
        :param company:
        """
        sql_1 = "SELECT * FROM customer WHERE account=?"
        sql_2 = "SELECT * FROM customer WHERE account=? AND company=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            # does the row exist with an account
            cur = db.cursor()
            cur.execute(sql_1, [account])
            cust = cur.fetchone()
            if cust:
                return dict(zip(self.model, cust))
            # does the row exist as 'NY'
            cur.execute(sql_2, ['NY', company])
            cust = cur.fetchone()
            if cust:
                return dict(zip(self.model, cust))
        # return empty
        return {}

    def insert_(self, values):
        """Insert a new customer
        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        sql = "INSERT INTO customer VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        if not type(values) == list or type(values) == tuple:
            values = list(values)
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()

    def insert_csv(self, filename, headers=False):
        """Import customer from csv file
        :param filename:
        :param headers:
        The expected file format contains data in the following sequence
        in : id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info
        """
        dbfn.recreate_table("customer")
        filename.encode("utf8")
        #      0  1   2    3    4    5       6    7         8   9     10  11    12  13  14  15
        # in : id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info
        # out: id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info att phon2 factor
        with open(filename) as csvdata:
            reader = csv.reader(csvdata)
            line = 0
            for row in reader:
                line += 1
                if headers and line == 1:
                    continue
                values = (row[0],
                          row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(), row[10].strip(),
                          row[11].strip(), row[12], row[13], row[14], row[15].strip(),
                          "", "", 0.0)
                self.insert_(values)

    def insert_http(self, values):
        """Insert a new customer
        :param values: List with values from http request
        expected incoming fields: acc comp add1 add2 zipcity country s_rep phone1 vat email att phon2
        """
        # check if exist - either as a real account or as a 'NY' account
        # adjust and call either update or insert as necessary
        #                  0   1    2    3    4       5       6     7      8   9     10  11
        # incoming fields: acc comp add1 add2 zipcity country s_rep phone1 vat email att phon2
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
        found = self.find_(values[0], values[1])
        if found:  # this is a complet customer with all fields
            if found["account"] == 'NY':
                found["account"] = values[0]
            if found["modified"] == 1:
                found["modified"] = 0
            found["company"] = values[1]
            found["address1"] = values[2]
            found["address2"] = values[3]
            found["zipcode"] = zipcode  # zipcity[4]
            found["city"] = city  # zipcity[4]
            # skip over country[5] and salesrep[6]
            found["phone1"] = values[7]
            found["vat"] = values[8]
            found["email"] = values[9]
            found["att"] = values[10]
            found["phone2"] = values[11]
            self.update_(found.values())  # call update function
        else:
            # in :    acc comp add1 add2   zipcity    country s_rep phon1 vat email att phon2
            # out: id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info att phon2 factor
            row_values = (None, values[0], values[1], values[2], values[3], zipcode, city, values[5],
                          values[6], values[7], values[8], values[9], 0, 0, 0, "", values[10], values[11], 0.0)
            # call insert function
            self.insert_(row_values)

    def load_(self):
        """Load customers into primary customer list"""
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            customers = cur.execute('SELECT * FROM customer')
            if customers:
                self.__customer_list = [dict(zip(self.model, row)) for row in customers]

    def save_(self):
        """Save current customer changes"""
        self.update_(self.current_customer.values())

    def update_(self, values):
        """Update current row
        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        sql = "UPDATE customer SET customerid=?, " \
              "account=?, company=?, address1=?, address2=?, zipcode=?, city=?, " \
              "country=?, salesrep=?, phone1=?, vat=?, email=?, deleted=?, modified=?, created=?, " \
              "infotext=?, att=?, phone2=?, factor=? " \
              "WHERE company=? AND phone1=?"
        if not type(values) == list or type(values) == tuple:
            values = list(values)
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, list(values))
            db.commit()
