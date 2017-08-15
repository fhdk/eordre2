#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Import customers http module"""
from PyQt5.QtCore import QThread

from util import httpfn
from util.status_communication import StatusCommunication

B_COLOR = "\033[0;33m"
E_COLOR = "\033[0;m"
DBG = True

__module__ = "import_customers_http"


def printit(string):
    """Print a variable string for debug purposes"""
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class ImportCustomersHttpThread(QThread):
    """
    Thread for importing customers using http
    """

    def __init__(self, customers, employees, settings, parent=None):
        """
        Initialize thread
        Args:
            customers:
            employees:
            settings:
            parent:
        """
        super(ImportCustomersHttpThread, self).__init__(parent)
        self.settings = settings  # main settings object
        self.employees = employees  # main employees object
        self.customers = customers  # main customer_list object
        self.comm = StatusCommunication()

    def run(self):
        """
        The run process - activated by the QTread start() method
        """
        self.comm.row_processing.emit("{}".format("Forbereder hentning ..."))
        # fetch datafile from http server
        data = httpfn.get_customers(self.settings,
                                    self.employees)
        self.comm.row_processing.emit("{}".format("Henter fra server ..."))
        self.comm.row_count.emit(len(data))
        for row in data:  # data processing
            self.comm.row_processing.emit("{}: {} - {}".format("Behandler", row[0], row[1]))
            self.customers.import_http(row)  # init_detail row to database
        self.comm.row_processing.emit("{}".format("   Færdig!"))
        self.comm.finished.emit()
