#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Report class"""

import csv
from datetime import datetime

from configuration import config
from models.query import Query
from models.report_calc import ReportCalc
from util import utils


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
            "id": "reportid",
            "fields": ("reportid", "employeeid", "repno", "repdate",
                       "newvisitday", "newdemoday", "newsaleday", "newturnoverday",
                       "recallvisitday", "recalldemoday", "recallsaleday", "recallturnoverday",
                       "sasday", "sasturnoverday", "demoday", "saleday",
                       "kmmorning", "kmevening", "supervisor", "territory",
                       "workday", "infotext", "sent", "offday", "offtext", "kmprivate", "created"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER NOT NULL", "INTEGER NOT NULL", "TEXT NOT NULL",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "REAL DEFAULT 0",
                      "INTEGER DEFAULT 0", "REAL DEFAULT 0", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0",
                      "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "TEXT", "TEXT",
                      "INTEGER DEFAULT 0", "TEXT", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0", "TEXT",
                      "INTEGER DEFAULT 0", "TEXT")
        }
        self._reports = []
        self._report = {}
        self.csv_field_count = 25
        self.q = Query()
        self.c = ReportCalc()
        if not self.q.exist_table(self.model["name"]):
            # build query and execute
            sql = self.q.build("create", self.model)
            success, data = self.q.execute(sql)
            if config.DEBUG_REPORT:
                print(
                    "\033[1;30m{}\n ->create table\n  ->success: {}\n  ->data: {}\033[1;m".format(
                        self.model["name"].upper(), success, data))

    @property
    def report(self):
        """
        Report
        Returns:
            Current report
        """
        return self._report

    @report.setter
    def report(self, workdate):
        """
        Set report to workdate
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

    def create(self, employee, workdate):
        """
        Create report for employee and date supplied
        Args:
            employee: object
            workdate: iso formatted str representing the report date
        """
        # we need to find the number of reports for the month of the supplied date
        # then add 1 to that number
        # we need to calculate the sums for the previous report for month
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
        aggregates = ["count(reportid) AS 'report_count'",
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
                      "(sum(newvisitday) + sum(recallvisitday)) AS 'visit'",
                      "(sum(newdemoday) + sum(recalldemoday)) AS 'demo'",
                      "(sum(newsaleday) +  sum(recallsaleday) + sum(sasday)) AS 'sale'",
                      "(sum(newturnoverday) + sum(recallturnoverday) + sum(sasturnoverday)) AS 'turnover'",
                      "(sum(kmevening - kmmorning)) AS 'kmwork'",
                      "(sum(kmprivate)) AS 'kmprivate'",
                      "(sum(workday = 1)) AS 'workdays'",
                      "(sum(offday = 1)) AS 'offdays'"]
        # filter on
        filteron = [("repdate", "LIKE", "and"), ("employeeid", "=", "and"), ("sent", "=")]
        # filter values
        ym_filter = "{}%".format(workdate[:8])
        values = (ym_filter, employee["employeeid"], 1)

        sql = self.q.build("select", self.model, aggregates=aggregates, filteron=filteron)

        if config.DEBUG_REPORT:
            print(
                "\033[1;30m{}\n ->create\n  ->aggregates: {}\n  ->sql: {}\n  ->values: {}\033[1;m".format(
                    self.model["name"].upper(), aggregates, sql, values))

        success, data = self.q.execute(sql, values)

        if config.DEBUG_REPORT:
            print(
                "\033[1;30m{}\n ->create\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

        if success and data:
            month = data[0]
            month = list(month)
            report_count = month[0]
            next_report = report_count + 1
            month = [workdate, "None", employee["employeeid"]] + list(month)
            created = datetime.today().isoformat()

            new_report = (None, employee["employeeid"], next_report, workdate,
                          None, None, None, None, None, None, None, None, None, None, None, None,
                          None, None, None, None, None, None, None, None, None, None, created)
            report_id = self.insert(new_report)
            month[1] = report_id
            month = tuple(month)
            if config.DEBUG_REPORT:
                print(
                    "\033[1;30m{}\n ->create\n  ->month: {}\033[1;m".format(
                        self.model["name"].upper(), month))
        else:
            return False

    def insert(self, values):
        """
        Insert new report in table
        """
        sql = self.q.build("insert", self.model)

        if config.DEBUG_REPORT:
            print(
                "\033[1;30m{}\n ->insert\n  ->sql: {}\n  ->values: {}\033[1;m".format(
                    self.model["name"].upper(), sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT:
            print(
                "\033[1;30m{}\n ->insert\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

        if success and data:
            return data
        return False

    def import_csv(self, filename, employee, headers=False):
        """
        Import report from file
        Args:
            filename: 
            employee: 
            headers: 
        """
        self.recreate_table()
        filename.encode("utf8")
        employeeid = employee["employeeid"]
        # open and read the file
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                if config.DEBUG_REPORT:
                    print(
                        "\033[1;30m{}\n ->import_csv\n  ->row: {}\033[1;m".format(
                            self.model["name"].upper(), row))
                if not len(row) == self.csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # translate bool text to integer for col 19, 21
                row[19] = utils.bool2int(utils.str2bool(row[19]))
                row[21] = utils.bool2int(utils.str2bool(row[21]))
                created = datetime.today().isoformat(sep="-")
                values = (row[0], employeeid, row[1], row[2].strip(),
                          row[3], row[4], row[5], row[6],
                          row[7], row[8], row[9], row[10],
                          row[11], row[12], row[13], row[14],
                          row[15], row[16], row[17].strip(), row[18].strip(),
                          row[19], row[20].strip(), row[21], row[22], row[23].strip(), row[24], created)
                if config.DEBUG_REPORT:
                    print(
                        "\033[1;30m{}\n ->import_csv\n  ->values: {}\033[1;m".format(
                            self.model["name"].upper(), values))
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
            print(
                "\033[1;30m{}\n ->insert\n  ->sql: {}\n  ->values: {}\033[1;m".format(
                    self.model["name"].upper(), sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT:
            print(
                "\033[1;30m{}\n ->insert\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

        if success and data:
            self._report = dict(zip(self.model["fields"], data))
            return True
        return False

    def load_reports(self, year=None, month=None):
        """
        Load report matching args or all if no args

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
            print(
                "\033[1;30m{}\n ->load_reports\n  ->sql: {}\n  ->values: {}\033[1;m".format(
                    self.model["name"].upper(), sql, values))

        success, data = self.q.execute(sql, values=values)

        if config.DEBUG_REPORT:
            print(
                "\033[1;30m{}\n ->load_reports\n  ->success: {}\n  ->data: {}\033[1;m".format(
                    self.model["name"].upper(), success, data))

        if success and data:
            self._reports = [dict(zip(self.model["fields"], row)) for row in data]
            return True

        self._reports = []
        return False

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
        Update report in database
        """
        # update_list = list(self.model["fields"])[1:]
        # update_where = [self.model["id"], "="]
        # self.q.values_to_arg(self._report.values())

        # if config.DEBUG_REPORT:
        #     print(
        #         "\033[1;30m{}\n ->update\n  ->sql: {}\n  ->values: {}\033[1;m".format(
        #             self.model["name"].upper(), sql, values))

        # if config.DEBUG_REPORT:
        #     print(
        #         "\033[1;30m{}\n ->update\n  ->success: {}\n  ->data: {}\033[1;m".format(
        #             self.model["name"].upper(), success, data))

        pass
