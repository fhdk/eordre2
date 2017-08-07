#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Visit details module
"""

from configuration import config
import csv

from models.query import Query
from util import utils

B_COLOR = "\033[1;30m"
E_COLOR = "\033[0;m"


def printit(string):
    print("{}{}{}".format(B_COLOR, string, E_COLOR))


class VisitDetail:
    """
    Visit details class
    """

    def __init__(self):
        """
        Initialize Saleine class
        """
        self.model = {
            "name": "current",
            "id": "detailid",
            "fields": ("detailid", "visitid", "pcs", "sku", "infotext", "price", "sas", "discount",
                       "linetype", "extra"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "INTEGER DEFAULT 0",
                      "TEXT", "TEXT", "REAL", "INTEGER DEFAULT 0", "REAL DEFAULT 0", "TEXT", "TEXT")
        }
        self._visitdetails = []
        self._visitdetail = {}
        self.csv_field_count = 8
        self.q = Query()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_SALELINE:
                printit("{}\n"
                        " ->table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(self.model["name"], success, data))

    @property
    def current(self):
        """
        Single current detail
        Returns:
             current
        """
        return self._visitdetail

    @property
    def visitdetails(self):
        """
        Visit details list
        Returns:
            List of details for a current
        """
        return self._visitdetails

    @visitdetails.setter
    def visitdetails(self, visitid):
        """
        Visit details setter. Load the details for at current
        Args:
            visitid:
        """
        try:
            _ = self._visitdetails[0]
        except IndexError:
            self.load(visitid)

    def clear(self):
        """
        Clear internal variables
        """
        self._visitdetail = {}
        self._visitdetails = []

    def create(self, visit_id):
        """
        Create a new detail on visitid
        Args:
            visit_id:
        """
        # create new with empty values
        values = (None, visit_id, None, "", "", None, None, None, None, None)

        detailid = self.insert(values)

        self._visitdetail = dict(zip(self.model["fields"], values))
        self._visitdetail["lineid"] = detailid
        self._visitdetails.append(self._visitdetail)

    def delete(self, detailid):
        """
        Delete the detail
        Args:
            detailid:
        """
        filters = [("detailid", "=")]
        values = (detailid,)

        sql = self.q.build("delete", self.model, filteron=filters)

        if config.DEBUG_SALELINE:
            printit("{}\n"
                    " ->delete\n"
                    "  ->filters: {}\n"
                    "  ->values: {}\n"
                    "  ->sql: {}".format(self.model["name"], filters, values, sql))

        success, data = self.q.execute(sql, values)

        if config.DEBUG_SALELINE:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))

        if success and data:
            return True
        return False

    def import_csv(self, filename, headers=False):
        """
        Import details from file
        Args:
            filename: csv file
            headers: flag first row as fieldnames
        """
        self.recreate_table()
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:

                if config.DEBUG_SALELINE:
                    printit("{}\n"
                            " ->import_csv\n"
                            "  ->row: {}".format(self.model["name"], row))

                if not len(row) == self.csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue

                # translate bool text to integer col 6
                row[6] = utils.bool2int(utils.str2bool(row[6]))
                values = (row[0], row[1], row[2], row[3].strip(), row[4].strip(), row[5], row[6], row[7], "s", None)

                if config.DEBUG_SALELINE:
                    printit("  ->{}\n"
                            "  ->values: {}".format(self.model["name"], values))

                self.insert(values)
            return True

    def insert(self, values):
        """
        Insert row
        Args:
            values:
        """
        sql = self.q.build("insert", self.model)

        if config.DEBUG_SALELINE:
            printit("{}\n"
                    " ->insert\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(self.model["name"], sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_SALELINE:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))

        if success and data:
            return data
        return False

    def load(self, visitid):
        """
        Load details for visitid
        """
        filters = [("visitid", "=")]
        values = [visitid]

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_SALELINE:
            printit("{}\n"
                    " ->load\n"
                    "  ->sql: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}".format(self.model["name"], sql, filters, values))

        success, data = self.q.execute(sql, values=values)

        if success and data:
            self.visitdetails = [dict(zip(self.model["fields"], row)) for row in data]

        if config.DEBUG_SALELINE:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))

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
        Write the current detail to database
        """
        fields = list(self.model["fields"])[1:]
        filters = [("lineid", "=")]
        values = self.q.values_to_arg(self._visitdetail.values())

        sql = self.q.build("update", self.model, update=fields, filteron=filters)

        if sql.startswith("ERROR"):
            printit("{}".format(sql))
            return False

        if config.DEBUG_SALELINE:
            printit("{}\n"
                    " ->load\n"
                    "  ->sql: {}\n"
                    "  ->fields: {}\n"
                    "  ->filters: {}\n"
                    "  ->values: {}".format(self.model["name"], sql, fields, filters, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_SALELINE:
            printit("  ->{}\n"
                    "  ->success: {}\n"
                    "  ->data: {}".format(self.model["name"], success, data))

        if success and data:
            return data
        return False
