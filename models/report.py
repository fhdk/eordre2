#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Report class"""

import csv
import sqlite3

from configuration import config
from util import dbfn


# noinspection PyMethodMayBeStatic
class Report:
    def __init__(self):
        """Initilize Report class"""
        # model for zipping dictionary
        self.model = (
            "reportid", "repno", "repdate",
            "newvisitday", "newdemoday", "newsaleday", "newturnoverday",
            "recallvisitday", "recalldemoday", "recallsaleday", "recallturnoverday",
            "sasday", "sasturnoverday", "demoday", "saleday",
            "kmmorning", "kmevening", "supervisor", "territory",
            "workday", "infotext", "sent", "offday", "offtext", "kmprivate")
        self.__reports = []
        self.__report = {}

    @property
    def current_report(self):
        return self.__report

    @current_report.setter
    def current_report(self, workdate):
        try:
            _ = self.__report["repdate"]
        except KeyError:
            self.load_report(workdate=workdate)

    @property
    def reportlist(self):
        return self.__reports

    @reportlist.setter
    def reportlist(self, year=None, month=None):
        self.__reports = []
        self.load_reports(year=year, month=month)

    def create_(self, employee, workdate):
        """Create report for employee and date supplied
        :param employee: object
        :param workdate: iso str representing the date for the report to be created
        """
        # we need to find the number of report for the month of the supplied date
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

        sql = "SELECT " \
              "sum(newvisitday) AS t_month_n_visit, " \
              "sum(newdemoday) AS t_month_n_demo, " \
              "sum(newsaleday) AS t_month_n_sale, " \
              "sum(newturnoverday) AS t_month_n_turnover, " \
              "sum(recallvisitday) AS t_month_r_visit, " \
              "sum(recalldemoday) AS t_month_r_demo, " \
              "sum(recallsaleday) AS t_month_r_sale, " \
              "sum(recallturnoverday) AS t_month_r_turnover, " \
              "sum(sasday) AS t_month_sas, " \
              "sum(sasturnoverday) AS t_month_sas_turnover, " \
              "(t_month_n_visit + t_month_r_visit) AS t_month_visit, " \
              "(t_month_n_demo + t_month_r_demo) AS t_month_demo, " \
              "(t_month_n_sale + t_month_r_sale + t_month_sas) AS t_month_sale, " \
              "(t_month_n_turnover + t_month_r_turnover + t_month_sas_turnover) AS t_month_turnover, " \
              "count(reportid) AS reportcount " \
              "FROM report WHERE repdate LIKE ? AND employeeid = ? ;"

        workmonth = (workdate[:8] + "%",)
        print("report -> create_ -> workdate: {}".format(workdate))
        print("report -> create_ -> workmonth: {}".format(workmonth))
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (workmonth, employee["employeeid"]))
            totals = cur.fetchone()
            print("report -> create_ -> select from report -> totals: {}".format(totals))

    def insert_(self, values):
        """Insert new report in table"""
        sql = "INSERT INTO report (" \
              "reportid, repno, repdate, " \
              "newvisitday, newdemoday, newsaleday, newturnoverday, " \
              "recallvisitday, recalldemoday, recallsaleday, recallturnoverday, " \
              "sasday, sasturnoverday, demoday, saleday, " \
              "kmmorning, kmevening, supervisor, territory, " \
              "workday, infotext, sent, offday, offtext, kmprivate) " \
              "VALUES (" \
              "?, ?, ?, " \
              "?, ?, ?, ?, " \
              "?, ?, ?, ?, " \
              "?, ?, ?, ?, " \
              "?, ?, ?, ?, " \
              "?, ?, ?, ?, ?, ?);"
        if not values:
            values = list(self.current_report.values())
        db = sqlite3.connect(config.DBPATH)
        with db:
            db.execute(sql, values)
            db.commit()

    def insert_csv(self, filename, headers=False):
        """Import report from file
        :param filename:
        :param headers:
        """
        # row: 0          1       2
        # csv: "reportid","repno","repdate",
        #      3             4            5            6
        #      "newvisitday","newdemoday","newsaleday","newturnoverday",
        #      7                8               9               10
        #      "recallvisitday","recalldemoday","recallsaleday","recallturnoverday",
        #      11       12               13        14
        #      "sasday","sasturnoverday","demoday","saleday",
        #      15          16          17           18
        #      "kmmorning","kmevening","supervisor","territory",
        #      19        20         21     22       23        24
        #      "workday","infotext","sent","offday","offtext","kmprivate"
        #
        dbfn.recreate_table("report")
        filename.encode("utf8")
        # open and read the file
        with open(filename) as csvdata:
            reader = csv.reader(csvdata)
            line = 0
            for row in reader:
                line += 1
                if headers and line == 1:
                    continue
                processed = [row[0].strip(), row[1], row[2].strip(),
                             row[3], row[4], row[5], row[6],
                             row[7], row[8], row[9], row[10],
                             row[11], row[12], row[13], row[14],
                             row[15], row[16], row[17].strip(), row[18].strip(),
                             row[19], row[20].strip(), row[21], row[22], row[23].strip(), row[24]]
                self.insert_(processed)

    def load_report(self, workdate):
        """Load report for supplied date
        :param workdate: iso formatted str representing the date for the report to be loaded
        """
        sql = "SELECT * FROM report WHERE repdate LIKE ?"
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (workdate,))
            report = cur.fetchone()
            if report:
                self.__report = dict(zip(self.model, report))

    def load_reports(self, year=None, month=None):
        """Load report matching year and month or all if no params are given
        :type year: str
        :type month: str
        """
        sql = "SELECT * FROM report"
        value = "{}-{}-{}".format("%", "%", "%")
        if year:
            sql = "SELECT * FROM report WHERE repdate LIKE ?"
            value = "{}-{}-{}".format(year, "%", "%")
        if year and month:
            sql = "SELECT * FROM report WHERE repdate LIKE ?"
            value = "{}-{}-{}".format(year, month, "%")
        db = sqlite3.connect(config.DBPATH)
        with db:
            cur = db.cursor()
            cur.execute(sql, (value,))
            reports = cur.fetchall()
            if reports:
                self.__reports = [dict(zip(self.model, row)) for row in reports]
            else:
                self.__reports = []