#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Orderhead class"""

import csv
import sqlite3

from configuration import config
from util import dbtablefn


# noinspection PyMethodMayBeStatic
class Visit:
    def __init__(self):
        """Initialize visits class"""
        # model for zipping dictionary
        self.model = (
            "visitid", "reportid", "employeeid", "customerid", "podate", "posent", "pocontact", "ponum", "pocompany",
            "poaddress1", "poaddress2", "popostcode", "popostoffice", "pocountry", "infotext", "proddemo", "prodsale",
            "ordertype", "turnsas", "turnsale", "turntotal", "approved")
        self.__visit_list_customer = []
        self.__visit_list_report = []
        self.__current_visit = {}

    @property
    def current_visit(self):
        return self.__current_visit

    @property
    def visit_list_customer(self):
        return self.__visit_list_customer

    @visit_list_customer.setter
    def visit_list_customer(self, orderid):
        try:
            _ = self.__visit_list_customer[0]
        except IndexError:
            self.__visit_list_customer = self.load_for_customer(customerid=orderid)

    @property
    def visit_list_report(self):
        return self.__visit_list_report

    @visit_list_report.setter
    def visit_list_report(self, orderid):
        try:
            _ = self.__visit_list_report[0]
        except IndexError:
            self.__visit_list_report = self.load_for_report(reportid=orderid)

    def add_(self):
        pass

    def create_(self, reportid, employeeid, customerid, workdate):
        self.__current_visit = {
            "approved": 0,
            "visitid": None,
            "reportid": reportid,
            "employeeid": employeeid,
            "customerid": customerid,
            "infotext": "",
            "podate": workdate,
            "posent": 0,
            "pocontact": "",
            "ponum": "",
            "pocompany": "",
            "poaddress1": "",
            "poaddress2": "",
            "popostcode": "",
            "popostoffice": "",
            "pocountry": "",
            "proddemo": "",
            "prodsale": "",
            "ordertype": "",
            "turnsale": "",
            "turnsas": "",
            "turntotal": ""
        }

    def find_(self, orderid):
        pass

    def insert_(self):
        """Save visits"""
        sql = "INSERT INTO visits VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = self.currentVisit.values()
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, values)
            db.commit()

    def insert_csv(self, filename, headers=False):
        """Import orders from file
        :param filename:
        :param headers:
        """
        sql = "INSERT INTO " \
              "visits (visitid, reportid, employeeid, customerid, podate, " \
              "posent, pocontact, ponum, pocompany, poaddress1, " \
              "poaddress2, popostcode, popostoffice, pocountry, infotext, " \
              "proddemo, prodsale, ordertype, turnsas, turnsale, " \
              "turntotal, approved) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        dbtablefn.drop_table("visits")
        dbtablefn.create_table("visits")
        db = sqlite3.connect(config.DBPATH)
        filename.encode("utf8")
        with db:
            with open(filename) as csvdata:
                reader = csv.reader(csvdata)
                line = 0
                for row in reader:
                    line += 1
                    if headers and line == 1:
                        continue
                    processed = [row[0], row[1], row[2], row[3], row[4].strip(),
                                 row[5], row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(),
                                 row[10].strip(), row[11].strip(), row[12].strip(), row[13].strip(), row[14].strip(),
                                 row[15].strip(), row[16].strip(), row[17].strip(), row[18], row[19],
                                 row[20], row[21]]
                    db.execute(sql, processed)
        db.commit()

    def load_for_customer(self, customerid):
        """Load orders for specified customer"""
        sql = "SELECT * FROM visits WHERE customerid=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (customerid,))
            visitss = cur.fetchall()
            if visitss:
                return [dict(zip(self.model, row)) for row in visitss]

    def load_for_report(self, reportid):
        """Load orders for specified customer"""
        sql = "SELECT * FROM visits WHERE reportid=?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (reportid,))
            visitss = cur.fetchall()
            if visitss:
                return [dict(zip(self.model, row)) for row in visitss]

    def update_(self, values):
        """Save current visits"""
        sql = "UPDATE visits SET orderid=?, reportid=?, employeeid=?, customerid=?, podate=?, " \
              "posent=?, pocontact=?, ponum=?, pocompany=?, poaddress1=?, poaddress2=?, " \
              "pozipcode=?, pocity=?, pocountry=?, infotext=?, proddemo=?, prodsale=?, " \
              "ordertype=?, turnsas=?, turnsale=?, turntotal=?, approved=? WHERE orderid=?;"
        values = values + [values[0]]
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, values)
            db.commit()
