#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Import customers csv module"""
import csv

from PyQt5.QtCore import QThread

from util.status_communication import StatusCommunication

B_COLOR = "\033[0;33m"
E_COLOR = "\033[0;m"
DBG = True

__module__ = "import_customers_csv"


def printit(string):
    """Print a variable string for debug purposes"""
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class ImportCustomersCsvThread(QThread):
    """
    Thread for importing customers using csv file
    """

    def __init__(self, customers, filename, headers, parent=None):
        """
        Initialize thread
        Args:
            customers:
            filename:
            parent:
        """
        super(ImportCustomersCsvThread, self).__init__(parent)
        self.customers = customers  # main customer_list object
        self.filename = filename.encode("utf8")
        self.header = headers
        self.comm = StatusCommunication()

    def run(self):
        """
        The run process - activated by the QTread start() method
        """
        self.comm.status.emit("{}".format("Forbereder indlæsning ..."))
        self.customers.recreate_table()
        ftext = "    Import er færdig!"
        with open(self.filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            rows = list(reader)
            # self.progress_c.rowcount.emit(len(rows))
            for line, row in enumerate(rows):
                if DBG:
                    printit("{}".format(row))
                if not len(row) == self.customers.csv_field_count:
                    ftext = "FEJL: Formatet i den valgte fil er ikke korrekt!"
                    break
                # self.progress_c.rowcount.emit(line)
                if self.header and line == 0:
                    continue
                self.comm.status.emit("{}: {} - {}".format("Behandler", row[1].strip(), row[2].strip()))
                self.customers.import_csv(row)  # send row to database

        self.comm.status.emit("{}".format(ftext))
        self.comm.done.emit()
