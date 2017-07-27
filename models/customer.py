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
from util import dbtablefn


class Customer:
    # last_mod -> _customers.txt
    # sample content: 2017-06-22 09:15:30
    # __customers.txt
    def __init__(self):
        """Initialize Customer class"""
        # model for zipping dictionary
        self.model = ("customerid",
                      "account", "company", "address1", "address2", "zipcode", "city",
                      "country", "salesrep", "phone1", "vat", "email",
                      "deleted", "modified", "created",
                      "infotext", "att", "phone2", "factor")

        self.__customers = []
        self.__customer = {}

    @property
    def currentcustomer(self):
        """Return current customer"""
        return self.__customer

    @property
    def customerlist(self):
        """Load customers into primary customer list"""
        try:
            _ = self.__customers[0]
        except IndexError:
            db = sqlite3.connect(config.DBPATH)
            with db:
                cur = db.cursor()
                cur.execute('SELECT * FROM customers')
                for row in cur:
                    c = dict(zip(self.model, row))
                    self.__customers.append(c)
        return self.__customers

    def add(self, customerdata):
        pass

    def find_(self, account, company):
        """Look up customer
        :param account:
        :param company:
        """
        sql_1 = "SELECT * FROM customers WHERE account=?"
        sql_2 = "SELECT * FROM customers WHERE account=? AND company=?"
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
        :param values: expecting a complete list with all fields
        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        sql = "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, values)
            db.commit()

    def insert_csv(self, filename, headers=False):
        """Import customers from csv file
        :param filename:
        :param headers:
        The expected file format contains data in the following sequence
        in : id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info
        """
        tablename = "customer"
        dbtablefn.drop_table(tablename)
        dbtablefn.create_table(tablename)
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
                values = [row[0],
                          row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(),
                          row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(), row[10].strip(),
                          row[11].strip(), row[12], row[13], row[14], row[15].strip(),
                          "", "", 0.0]
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
        p = values[4].find(" ")
        n = values[4][:p] + "|" + values[4][p:]
        zipcity = n.split("|")
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
            # extract values from customer
            row_values = list(found.values())
            # call update function
            self.update_(row_values)
        else:
            # sql = "SELECT customerid FROM customers ORDER BY customerid DESC LIMIT 1;"
            # db = sqlite3.connect(config.DBPATH)
            # with db:
            #     cur = db.cursor()
            #     cur.execute(sql)
            #     lastid = cur.fetchone()
            #     if lastid:
            #         newid = lastid[0] + 1
            #     else:
            #         newid = 1
            # in :    acc comp add1 add2   zipcity    country s_rep phon1 vat email att phon2
            # out: id acc comp add1 add2 zipcode city country s_rep phon1 vat email del mod cre info att phon2 factor
            row_values = [None, values[0], values[1], values[2], values[3], zipcode, city, values[5],
                          values[6], values[7], values[8], values[9], 0, 0, 0, "", values[10], values[11], 0.0]
            # call insert function
            self.insert_(row_values)

    def update_(self, values):
        """Update current row
        :param values: expecting a complete list with all fields
        db : id acc comp add1 add2 zip city country s_rep phon1 vat email del mod cre info att phon2 factor
        """
        sql = "UPDATE customers SET customerid=?, " \
              "account=?, company=?, address1=?, address2=?, zipcode=?, city=?, " \
              "country=?, salesrep=?, phone1=?, vat=?, email=?, deleted=?, modified=?, created=?, " \
              "infotext=?, att=?, phone2=?, factor=? " \
              "WHERE customerid=?"
        db = sqlite3.connect(config.DBPATH)
        values.append(values[0])
        with db:
            cur = db.cursor()
            cur.execute(sql, values)
            db.commit()
