#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Import products module"""

from PyQt5.QtCore import QThread

from util import httpfn
from util.status_communication import StatusCommunication


class ImportProductsThread(QThread):
    """
    Thread for importing product using http
    """

    def __init__(self, products, settings, parent=None):
        """
        Initialize the thread
        Args:
            products:
            settings:
            parent:
        """
        super(ImportProductsThread, self).__init__(parent)
        self.settings = settings  # assign current object
        self.products = products  # assign product object
        self.comm = StatusCommunication()

    def run(self):
        """
        The run process - activated by the QTread start() method
        """
        self.comm.status.emit("{}".format("Forbereder hentning ..."))
        self.products.drop_table()  # drop product table
        self.comm.status.emit("{}".format("Henter fra server ..."))
        # fetching datafile from http server
        data = httpfn.get_products(self.settings)
        self.comm.count.emit(len(data))
        for row in data:  # data processing
            self.comm.status.emit("{}: {} - {}".format("Behandler", row[0], row[1]))
            self.products.insert(row)  # init_detail row to database
        self.comm.status.emit("{}".format("   Færdig!"))
        self.comm.done.emit()
