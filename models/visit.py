#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Visit module
"""

import csv

from configuration import config
from models.query import Query
from util import utils

B_COLOR = "\033[1;36m"
E_COLOR = "\033[0;1m"

__module__ = "visit"


def printit(string):
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


# noinspection PyMethodMayBeStatic
class Visit:
    """
    Visit class
    """

    def __init__(self):
        """
        Initialize current class
        """
        self.model = {
            "name": "visit",
            "id": "visit_id",
            "fields": ("visit_id", "report_id", "employee_id", "customer_id", "visit_date", "po_sent",
                       "po_buyer", "po_number", "po_company", "po_address1", "po_address2",
                       "po_postcode", "po_postoffice", "po_country",
                       "info_text", "prod_demo", "prod_sale", "visit_type",
                       "po_sas", "po_sale", "po_total", "po_approved"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "INTEGER NOT NULL", "INTEGER NOT NULL",
                      "TEXT NOT NULL", "INTEGER DEFAULT 0",
                      "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT",
                      "TEXT NOT NULL", "REAL DEFAULT 0", "REAL DEFAULT 0", "REAL DEFAULT 0", "INTEGER DEFAULT 0")
        }
        self._report_visits = []
        self._visit = {}
        self._customer_visits = []
        self._csv_field_count = 22
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_VISIT:
                printit(" ->table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))

    @property
    def active(self):
        """
        Visit
        Returns:
            The current active visit
        """
        return self._visit

    @active.setter
    def active(self, visit_id):
        """
        Set a visit
        :param visit_id:
        :return:
        """
        self.find(visit_id)

    @property
    def visit_list_customer(self):
        """
        The list of visits for a customer
        Returns:
            The list of visits for a customer
        """
        return self._customer_visits

    @visit_list_customer.setter
    def visit_list_customer(self, customer_id):
        """
        Load the list of visits for a customer_id
        Args:
            customer_id:
        """
        self.load_for_customer(customer_id)

    @property
    def visit_list_report(self):
        """
        Report Visit List
        Returns:
            The list of visits for a report_id
        """
        return self._report_visits

    @visit_list_report.setter
    def visit_list_report(self, report_id):
        """
        Load visits for the requested report_id
        Args:
            report_id:
        """
        self.load_for_report(report_id)

    def clear(self):
        """
        Clear internal variables
        """
        self._visit = {}
        self._report_visits = []
        self._customer_visits = []

    def add(self, report_id, employee_id, customer_id, workdate):
        """
        Create a new visit
        Args:
            report_id:
            employee_id:
            customer_id:
            workdate:
        """
        values = (None, report_id, employee_id, customer_id, workdate, 0,
                  "", "", "", "", "", "", "", "", "", "", "", "", 0.0, 0.0, 0.0, 0)
        new_id = self.insert(values)
        self.find(new_id)
        self._customer_visits.append(self._visit)
        self._report_visits.append(self._visit)

    def delete(self, visit_id):
        """
        Delete the specified visit
        :param visit_id:
        :return:
        """
        filters = [(self.model["id"], "=")]
        values = (visit_id,)
        sql = self.q.build("delete", self.model, filters)
        self.q.execute(sql, values)

    def find(self, visit_id):
        """
        Find the specified visit
        :param visit_id:
        :return:
        """
        filters = [(self.model["id"], "=")]
        values = (visit_id,)
        sql = self.q.build("select", self.model, filters=filters)
        if config.DEBUG_VISIT:
            printit(" ->find\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_VISIT:
            printit("  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        if success:
            try:
                self._visit = dict(zip(self.model["fields"], data[0]))
                return True
            except IndexError:
                self._visit = {}
        return False

    def import_csv(self, filename, headers=False):
        """
        Import orders from file
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
                if not len(row) == self._csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # translate bool text to integer col 5
                row[5] = utils.bool2int(utils.arg2bool(row[5]))
                values = (row[0], row[1], row[2], row[3], row[4].strip(),
                          row[5], row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(),
                          row[10].strip(), row[11].strip(), row[12].strip(), row[13].strip(), row[14].strip(),
                          row[15].strip(), row[16].strip(), row[17].strip(), row[18], row[19],
                          row[20], row[21])
                self.insert(values)  # call insert function
            return True

    def insert(self, values):
        """
        Insert a new row in the database
        Args:
            values:
        """
        sql = self.q.build("insert", self.model)
        if config.DEBUG_VISIT:
            printit(" ->insert\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_VISIT:
            printit("  ->success: {}\n "
                    "  ->data: {}".format(success, data))
        if success and data:
            return data
        return False

    def load_for_customer(self, customer_id):
        """
        Load visit_list_customer for specified customer
        Args:
            customer_id:
        """
        filters = [("customer_id", "=")]
        values = (customer_id,)
        sql = self.q.build("select", self.model, filters=filters)
        if config.DEBUG_VISIT:
            printit(" ->load_for_customer\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_VISIT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success:
            try:
                self._customer_visits = [dict(zip(self.model["fields"], row)) for row in data]
                self._visit = self._customer_visits[0]
            except (IndexError, KeyError):
                self._visit = {}
                self._customer_visits = []

    def load_for_report(self, report_id):
        """
        Load visit_list_customer for specified report
        Args:
            report_id:
        """
        filters = [("report_id", "=")]
        values = (report_id,)
        sql = self.q.build("select", self.model, filters=filters)
        if config.DEBUG_VISIT:
            printit(" ->load_for_report\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(filters, values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_VISIT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success:
            try:
                self._report_visits = [dict(zip(self.model["fields"], row)) for row in data]
                self._visit = self._report_visits[0]
            except (IndexError, KeyError):
                self._visit = {}
                self._report_visits = []

    def recreate_table(self):
        """
        Recreate table
        """
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
        self.clear()

    def update(self):
        """
        Write visit changes to database
        """
        fields = list(self.model["fields"])[1:]
        filters = [(self.model["id"], "=")]
        values = self.q.values_to_arg(self._visit.values())
        sql = self.q.build("update", self.model, update=fields, filters=filters)
        if config.DEBUG_VISIT:
            printit(" ->update\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(fields, filters, values, sql))
        success, data = self.q.execute(sql, values=values)
        if config.DEBUG_VISIT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))
        if success and data:
            return data
        return False
