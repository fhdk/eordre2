#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt5.QtCore import QThread, pyqtSignal, QObject

from models import customer, product
from util import httpfn


class Communicate(QObject):
    processing = pyqtSignal(str)  # status message signal
    rowcount = pyqtSignal(int)  # rowcount signal
    finished = pyqtSignal()  # finished signal


class ImportCustomersThread(QThread):
    """Thread for importing customer through http"""

    def __init__(self, settings, employee, parent=None):
        super(ImportCustomersThread, self).__init__(parent)
        self.settings = settings  # assign settings object
        self.employee = employee  # assign employee object
        self.Customer = customer.Customer()  # create_ customer object
        self.c = Communicate()

    def run(self):
        """The run process - activated by the QTread start() method"""
        self.c.processing.emit("{}".format("Forbereder hentning ..."))
        # fetch datafile from http server
        data = httpfn.get_customers(self.settings, self.employee)
        self.c.processing.emit("{}".format("Henter fra server ..."))
        self.c.rowcount.emit(len(data))
        for row in data:  # data processing
            self.c.processing.emit("{}: {} - {}".format("Behandler", row[0], row[1]))
            self.Customer.insert_http(row)  # add row to database
        self.c.processing.emit("{}".format("   Færdig!"))
        self.c.finished.emit()


class ImportProductsThread(QThread):
    """Thread for importing product through http"""

    def __init__(self, settings, parent=None):
        super(ImportProductsThread, self).__init__(parent)
        self.settings = settings  # assign settings object
        self.Product = product.Product()  # create_ product object
        self.c = Communicate()

    def run(self):
        """The run process - activated by the QTread start() method"""
        self.c.processing.emit("{}".format("Forbereder hentning ..."))
        self.Product.drop_table()  # drop product table
        self.c.processing.emit("{}".format("Henter fra server ..."))
        # fetching datafile from http server
        data = httpfn.get_product(self.settings)
        self.c.rowcount.emit(len(data))
        for row in data:  # data processing
            self.c.processing.emit("{}: {} - {}".format("Behandler", row[0], row[1]))
            self.Product.insert_(row)  # add row to database
        self.c.processing.emit("{}".format("   Færdig!"))
        self.c.finished.emit()
