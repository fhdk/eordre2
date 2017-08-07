#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Threads module
"""

from PyQt5.QtCore import QThread, pyqtSignal, QObject

from util import httpfn


class Communicate(QObject):
    """
    Communication Object
    """
    processing = pyqtSignal(str)  # status message signal
    rowcount = pyqtSignal(int)  # rowcount signal
    finished = pyqtSignal()  # finished signal


class ImportCustomersThread(QThread):
    """
    Thread for importing current through http
    """
    def __init__(self, customers, employees, settings, parent=None):
        """
        Initialize thread
        Args:
            customers: main current object
            employees: main employeeid object
            settings: main current object
            parent:
        """
        super(ImportCustomersThread, self).__init__(parent)
        self.settings = settings  # main settings object
        self.employees = employees  # main employees object
        self.customers = customers  # main customers object
        self.c = Communicate()

    def run(self):
        """
        The run process - activated by the QTread start() method
        """
        self.c.processing.emit("{}".format("Forbereder hentning ..."))
        # fetch datafile from http server
        data = httpfn.get_customers(self.settings.current,
                                    self.employees.current)
        self.c.processing.emit("{}".format("Henter fra server ..."))
        self.c.rowcount.emit(len(data))
        for row in data:  # data processing
            self.c.processing.emit("{}: {} - {}".format("Behandler", row[0], row[1]))
            self.customers.import_http(row)  # create row to database
        self.c.processing.emit("{}".format("   Færdig!"))
        self.c.finished.emit()


class ImportProductsThread(QThread):
    """
    Thread for importing product through http
    """
    def __init__(self, products, settings, parent=None):
        """
        Initialize the thread
        Args:
            parent:
        """
        super(ImportProductsThread, self).__init__(parent)
        self.settings = settings  # assign current object
        self.products = products  # assign product object
        self.c = Communicate()

    def run(self):
        """
        The run process - activated by the QTread start() method
        """
        self.c.processing.emit("{}".format("Forbereder hentning ..."))
        self.product.drop_table()  # drop product table
        self.c.processing.emit("{}".format("Henter fra server ..."))
        # fetching datafile from http server
        data = httpfn.get_products(self.settings)
        self.c.rowcount.emit(len(data))
        for row in data:  # data processing
            self.c.processing.emit("{}: {} - {}".format("Behandler", row[0], row[1]))
            self.products.insert(row)  # create row to database
        self.c.processing.emit("{}".format("   Færdig!"))
        self.c.finished.emit()
