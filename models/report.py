#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Report class"""

from pprint import pprint

import csv

from util.query import Query
from models.report_calc import ReportCalc
from util import dbfn, utils


# noinspection PyMethodMayBeStatic
class Report:
    def __init__(self):
        """Initilize Report class"""
        self.model = {
            "name": "report",
            "id": "reportid",
            "fields": ("reportid", "employeeid", "repno", "repdate",
                       "newvisitday", "newdemoday", "newsaleday", "newturnoverday",
                       "recallvisitday", "recalldemoday", "recallsaleday", "recallturnoverday",
                       "sasday", "sasturnoverday", "demoday", "saleday",
                       "kmmorning", "kmevening", "supervisor", "territory",
                       "workday", "infotext", "sent", "offday", "offtext", "kmprivate"),
            "types": ("INTEGER PRIMARY KEY NOT NULL", "INTEGER", "INTEGER", "TEXT",
                      "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "INTEGER", "INTEGER", "REAL",
                      "INTEGER", "REAL", "INTEGER", "INTEGER",
                      "INTEGER", "INTEGER", "TEXT", "TEXT",
                      "INTEGER", "TEXT", "INTEGER", "INTEGER", "TEXT", "INTEGER")
        }
        self._reports = []
        self._report = {}
        self._totals = {}
        self.csv_field_count = 25
        self.q = Query()
        if not dbfn.exist_table(self.model["name"]):
            sql = self.q.build("create", self.model)
            self.q.execute(sql)

    @property
    def current_report(self):
        return self._report

    @current_report.setter
    def current_report(self, workdate):
        try:
            _ = self._report["repdate"]
        except KeyError:
            self.load_report(workdate=workdate)

    @property
    def reportlist(self):
        return self._reports

    @reportlist.setter
    def reportlist(self, year=None, month=None):
        self._reports = []
        self.load_reports(year=year, month=month)

    def create(self, employee, workdate):
        """Create report for employee and date supplied
        :param employee: object
        :param workdate: iso formatted str representing the report date
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

        # sql = "SELECT " \
        #       "sum(newvisitday) AS 'new_visit', " \
        #       "sum(newdemoday) AS 'new_demo', " \
        #       "sum(newsaleday) AS 'new_sale', " \
        #       "sum(newturnoverday) AS 'new_turnover', " \
        #       "sum(recallvisitday) AS 'recall_visit', " \
        #       "sum(recalldemoday) AS 'recall_demo', " \
        #       "sum(recallsaleday) AS 'recall_sale', " \
        #       "sum(recallturnoverday) AS 'recall_turnover', " \
        #       "sum(sasday) AS 'sas', " \
        #       "sum(sasturnoverday) AS 'sas_turnover', " \
        #       "(sum(newvisitday) + sum(recallvisitday)) AS 'visit', " \
        #       "(sum(newdemoday) + sum(recalldemoday)) AS 'demo', " \
        #       "(sum(newsaleday) +  sum(recallsaleday) + sum(sasday)) AS 'sale', " \
        #       "(sum(newturnoverday) + sum(recallturnoverday) + sum(sasturnoverday)) AS 'turnover', " \
        #       "(sum(kmevening - kmmorning)) AS 'kmwork', " \
        #       "(sum(kmprivate)) AS 'kmprivate', " \
        #       "(sum(workday = 1)) AS 'workdays', " \
        #       "(sum(offday = 1)) AS 'offdays', " \
        #       "count(reportid) AS 'reports' " \
        #       "FROM report WHERE repdate LIKE ? AND employeeid=? ;"
        # 
        # values = [workdate[:8] + "%", employee["employeeid"]]

        aggregate_list = ["sum(newvisitday) AS 'new_visit'",
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
                          "(sum(offday = 1)) AS 'offdays'",
                          "count(reportid) AS 'reports'"]
        where_list = [("repdate", "LIKE", "'" + workdate[:8] + "%'"), ("employeeid", "=", employee["employeeid"])]

        sql = self.q.build("select", self.model, aggregate_list=aggregate_list, where_list=where_list)

        totals = self.q.execute(sql)

        totals = [workdate, "None", employee["employeeid"]] + list(totals)
        self._totals = dict(zip(self.model["fields"], totals))
        new_values = [None, employee["employeeid"], (self._totals["reports"] + 1), workdate,
                      None, None, None, None, None, None, None, None, None, None, None, None,
                      None, None, None, None, None, None, None, None, None, None]
        self._totals["reportid"] = self.insert(new_values)

        calc = ReportCalc()


        # db = sqlite3.connect(config.DBPATH)
        # with db:
        #     cur = db.cursor()
        #     cur.execute(sql, values)
        #     totals = cur.fetchone()
        #     totals = [workdate, "None", employee["employeeid"]] + list(totals)
        #     print(totals)
        #     self.__totals = dict(zip(self.totals_model["fields"], totals))
        #     new_values = [None, employee["employeeid"], (self.__totals["reports"] + 1), workdate,
        #                   None, None, None, None, None, None, None, None, None, None, None, None,
        #                   None, None, None, None, None, None, None, None, None, None]
        #     self.__totals["reportid"] = self.insert(new_values)
        #
        # print("TODO: add report in database!")

    def insert(self, values):
        """Insert new report in table"""
        value_list = values
        sql = self.q.build("insert", self.model)
        if not type(values) == list:
            value_list = list(values)
        return self.q.execute(sql, value_list=value_list)

    def import_csv(self, filename, employee, headers=False):
        """Import report from file
        :param filename:
        :param employee:
        :param headers:
        """
        dbfn.recreate_table("report")
        filename.encode("utf8")
        employeeid = employee["employeeid"]
        # open and read the file
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                if not len(row) == self.csv_field_count:
                    return False
                line += 1
                if headers and line == 1:
                    continue
                # translate bool text to integer for col 19, 21
                row[19] = utils.bool2int(utils.str2bool(row[19]))
                row[21] = utils.bool2int(utils.str2bool(row[21]))
                processed = [row[0], employeeid, row[1], row[2].strip(),
                             row[3], row[4], row[5], row[6],
                             row[7], row[8], row[9], row[10],
                             row[11], row[12], row[13], row[14],
                             row[15], row[16], row[17].strip(), row[18].strip(),
                             row[19], row[20].strip(), row[21], row[22], row[23].strip(), row[24]]
                self.insert(processed)
            return True

    def load_report(self, workdate):
        """Load report for supplied date
        :param workdate: iso formatted str representing the date for the report to be loaded
        """
        where_list = [("repdate", "like")]
        sql = self.q.build("select", self.model, where_list=where_list)
        value_list = [workdate]
        result = self.q.execute(sql, value_list=value_list)
        if result:
            self._report = dict(zip(self.model["fields"], result))

    def load_reports(self, year=None, month=None):
        """Load report matching year and month or all if no params are given
        :type year: str
        :type month: str
        """
        where_list = ["repdate", "like"]
        sql = self.q.build("select", self.model, where_list=where_list)
        value = "{}-{}-{}".format("%", "%", "%")
        if year:
            value = "{}-{}-{}".format(year, "%", "%")
        if year and month:
            value = "{}-{}-{}".format(year, month, "%")
        value_list = [value]
        result = self.q.execute(sql, value_list=value_list)
        if result:
            self._reports = [dict(zip(self.model["fields"], row)) for row in result]
        else:
            self._reports = []

    def update_report(self):
        pass

    def save_totals(self):
        pass
