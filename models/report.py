#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Report class"""

__module__ = "report"

import csv
from datetime import datetime

from configuration import config
from models.query import Query
from models.report_calculator import Calculator
from util import utils

B_COLOR = "\033[0;37m"
E_COLOR = "\033[0;m"


def printit(string):
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


# noinspection PyMethodMayBeStatic
class Report:
    """
    Report
    """

    def __init__(self):
        """
        Initilize Report class
        """
        self.model = {
            "name": "report",
            "id": "report_id",
            "fields": ("report_id", "employee_id", "repno", "repdate", "timestamp",
                       "newvisitday", "newdemoday", "newsaleday", "newturnoverday",
                       "recallvisitday", "recalldemoday", "recallsaleday", "recallturnoverday",
                       "sasday", "sasturnoverday", "demoday", "saleday",
                       "kmmorning", "kmevening", "supervisor", "territory",
                       "workday", "infotext", "sent", "offday", "offtext", "kmprivate"),
            "types": ("INTEGER PRIMARY KEY NOT NULL",
                      "INTEGER NOT NULL", "INTEGER NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "REAL DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "TEXT", "TEXT",
                      "INTEGER DEFAULT 0", "TEXT", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "TEXT",
                      "INTEGER DEFAULT 0")
        }
        self._reports = []
        self._report = {}
        self._csv_field_count = 25
        self.q = Query()
        self.c = Calculator()
        if not self.q.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_REPORT:
                printit(" ->init_detail table\n"
                        "  ->success: {}\n"
                        "  ->data: {}".format(success, data))

    @property
    def current(self):
        """
        Report
        Returns:
            Current reportid
        """
        return self._report

    @current.setter
    def current(self, workdate):
        """
        Set reportid to workdate
        Args:
            workdate:
        """
        try:
            _ = self._report["repdate"]
        except KeyError:
            self.load_report(workdate=workdate)

    @property
    def reportlist(self):
        """
        Report List
        Returns:
            Current list of reports
        """
        return self._reports

    @reportlist.setter
    def reportlist(self, year=None, month=None):
        """
        Set the current list of reports to specified filter
        Args:
            year:
            month:
        """
        self._reports = []
        self.load_reports(year=year, month=month)

    def clear(self):
        """
        Clear internal variables
        """
        self.c.clear()
        self._report = {}
        self._reports = []

    def create(self, employee, workdate):
        """
        Create reportid for employeeid and date supplied
        Args:
            employee: object
            workdate: iso formatted str representing the reportid date
        """
        # we need to find the number of reports for the month of the supplied date
        # then init_detail 1 to that number
        # we need to calculate the sums for the previous reportid for month
        # those sums will be stored in seperate table
        # creating a new table with
        #           sum demoes & sum sales
        # |  *  |              DAY               |             MONTH              |
        # | --- | ------------------------------ | ------------------------------ |
        # |  *  | Visit | Demo | Sale | Turnover | Visit | Demo | Sale | Turnover |
        # | --- | ------------------------------ | ------------------------------ |
        # |  N  |  sum     sum   sum      sum       sum     sum    sum    sum
        # |  R  |  sum     sum   sum      sum       sum     sum    sum    sum
        # | SAS |                sum      sum                      sum    sum
        # | SUM |  sum     sum   sum      sum       sum     sum    sum    sum

        # parameters for initial feed of ReportCalc
        # aggregates
        aggregates = ["count(report_id) AS 'report_count'",
                      "sum(newvisitday) AS 'new_visit'",
                      "sum(newdemoday) AS 'new_demo'",
                      "sum(newsaleday) AS 'new_sale'",
                      "sum(newturnoverday) AS 'new_turnover'",
                      "sum(recallvisitday) AS 'recall_visit'",
                      "sum(recalldemoday) AS 'recall_demo'",
                      "sum(recallsaleday) AS 'recall_sale'",
                      "sum(recallturnoverday) AS 'recall_turnover'",
                      "sum(sasday) AS 'sas'",
                      "sum(sasturnoverday) AS 'sas_turnover'",
                      "(sum(newvisitday) + sum(recallvisitday)) AS 'current'",
                      "(sum(newdemoday) + sum(recalldemoday)) AS 'demo'",
                      "(sum(newsaleday) +  sum(recallsaleday) + sum(sasday)) AS 'sale'",
                      "(sum(newturnoverday) + sum(recallturnoverday) + sum(sasturnoverday)) AS 'turnover'",
                      "(sum(kmevening - kmmorning)) AS 'kmwork'",
                      "(sum(kmprivate)) AS 'kmprivate'",
                      "(sum(workday = 1)) AS 'workdays'",
                      "(sum(offday = 1)) AS 'offdays'"]
        filters = [("repdate", "LIKE", "and"), ("employee_id", "=", "and"), ("sent", "=")]
        ym_filter = "{}%".format(workdate[:8])
        employee_id = employee["employee_id"]
        values = (ym_filter, employee_id, 1)

        sql = self.q.build("select", self.model, aggregates=aggregates, filteron=filters)

        if config.DEBUG_REPORT:
            printit(" ->init_detail\n"
                    "  ->aggregates: {}\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(aggregates, sql, values))

        success, data = self.q.execute(sql, values)

        if config.DEBUG_REPORT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success and data:
            # assign expected result from list item
            try:
                _ = data[0]
            except IndexError:
                return False
            # temporary convert tuple to list
            current_month_totals = list(data[0])
            # extract report count from first column
            report_count = int(current_month_totals[0])
            # increment report count
            next_report = report_count + 1
            # init_detail a combined list with the identifiers and the totals
            current_month_totals = [workdate, "None", employee_id] + current_month_totals
            timestamp = datetime.today()
            # init_detail tuple with values to initialze the new report
            new_report_values = (None, employee_id, next_report, workdate, timestamp,
                                 None, None, None, None, None, None, None, None, None, None, None, None,
                                 None, None, None, None, None, None, None, None, None, None)
            # assign return value as new report_id
            report_id = self.insert(new_report_values)
            # insert report_id to identify for which report the totals was calculated
            current_month_totals[1] = report_id
            # revert to tuple
            current_month_totals = tuple(current_month_totals)
            if config.DEBUG_REPORT:
                printit("  ->month: {}".format(current_month_totals))
            # insert the values in the calculation table
            self.c.insert(current_month_totals)
            return True
        else:
            return False

    def insert(self, values):
        """
        Insert new reportid in table
        """
        sql = self.q.build("insert", self.model)

        if config.DEBUG_REPORT:
            printit(" ->insert\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success and data:
            return data
        return False

    def import_csv(self, filename, employee_id, headers=False):
        """
        Import reportid from file
        Args:
            filename: 
            employee_id:
            headers: 
        """
        self.recreate_table()
        filename.encode("utf8")
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:

                if config.DEBUG_REPORT:
                    printit(" ->import_csv\n"
                            "  ->row: {}".format(row))

                if not len(row) == self._csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # translate bool text to integer for col 19, 21
                row[19] = utils.bool2int(utils.str2bool(row[19]))
                row[21] = utils.bool2int(utils.str2bool(row[21]))
                # init_detail a timestamp
                local_timestamp = datetime.today()
                values = (row[0], employee_id, row[1], row[2].strip(), row[3], local_timestamp,
                          row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12],
                          row[13], row[14], row[15], row[16], row[17].strip(), row[18].strip(),
                          row[19], row[20].strip(), row[21], row[22], row[23].strip(), row[24])

                if config.DEBUG_REPORT:
                    printit("  ->values: {}".format(values))
                self.insert(values)
            return True

    def load_report(self, workdate):
        """
        Load report for supplied date arg

        Args:
            workdate: iso formatted str representing the date for the report to be loaded
        """
        filters = [("repdate", "=")]
        values = (workdate,)

        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_REPORT:
            printit(" ->load_report\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT:
            printit("  ->success: {}\n  ->data: {}".format(success, data))

        if success:
            try:
                self._report = dict(zip(self.model["fields"], data[0]))
                return True
            except IndexError:
                self._report = {}

        return False

    def load_reports(self, year=None, month=None):
        """
        Load reports matching args or all if no args

        Args:
            :type year: str
            :type month: str
        """
        filters = ["repdate", "like"]
        value = "{}-{}-{}".format("%", "%", "%")
        if year:
            value = "{}-{}-{}".format(year, "%", "%")
        if year and month:
            value = "{}-{}-{}".format(year, month, "%")
        values = (value,)
        sql = self.q.build("select", self.model, filteron=filters)

        if config.DEBUG_REPORT:
            printit(" ->load_reports\n"
                    "  ->sql: {}\n"
                    "  ->values: {}".format(sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT:
            printit("  ->success: {}\n"
                    "  ->data: {}".format(success, data))

        if success:
            try:
                _ = data[0]
                self._reports = [dict(zip(self.model["fields"], row)) for row in data]
                return True
            except IndexError:
                self._reports = []
        return False

    def recreate_table(self):
        """
        Drop and init_detail table
        """
        self.c.recreate_table()
        sql = self.q.build("drop", self.model)
        self.q.execute(sql)
        sql = self.q.build("create", self.model)
        self.q.execute(sql)
        self.clear()

    def update(self):
        """
        Update reportid in database
        """
        # update_list = list(self.model["fields"])[1:]
        # update_where = [(self.model["id"], "=")]
        # self.q.values_to_arg(self._report.values())

        # if config.DEBUG_REPORT:
        #     printit(
        #         "{}\n ->update\n  ->sql: {}\n  ->values: {}".format(
        #             sql, values))

        # if config.DEBUG_REPORT:
        #     printit(
        #         "{}\n ->update\n  ->success: {}\n  ->data: {}".format(
        #             success, data))

        pass
