#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt5.QtWidgets import QDialog

from util.import_products import ImportProductsThread
from util.status_communication import StatusCommunication
from resources.get_products_http_dialog_rc import Ui_getProductsHttpDialog


class GetProductsHttpDialog(QDialog, Ui_getProductsHttpDialog):
    """
    Dialog for importing products from server
    """

    def __init__(self, products, settings, parent=None):
        """
        Initialize Dialog
        Args:
            products: main product object
            settings: main current object
        """
        super(GetProductsHttpDialog, self).__init__(parent)
        self.setupUi(self)
        self.comm = StatusCommunication()
        self.progresscount = 1  # Used when setting progress values
        self.counter = 0  # Used when setting progress values
        self.rowcounter = 0  # Used when updating the status listbox
        self.thread = ImportProductsThread(products=products, settings=settings)
        # connect signals
        self.buttonStart.clicked.connect(self.button_start_clicked)
        self.buttonClose.clicked.connect(self.button_close_clicked)

    def add_row(self, text):
        """Slot for import thread processing signal"""
        self.itemList.addItem(text)
        self.itemList.setCurrentRow(self.rowcounter)
        self.rowcounter += 1

        if self.progresscount == self.counter:
            self.counter = 0
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        else:
            self.counter += 1

    def button_close_clicked(self):
        """Slot for buttonClose clicked signal"""
        self.done(True)

    def button_start_clicked(self):
        """Slot for buttonStart clicked signal"""
        self.progress_bar.setValue(0)
        # connect to the thread signals
        self.thread.comm.processing.connect(self.add_row)
        self.thread.comm.finished.connect(self.threaddone)
        self.thread.comm.rowcount.connect(self.set_progressbar)
        # start the thread
        self.thread.start()
        # we don't want to double the processes or close before finished
        self.buttonStart.setEnabled(False)
        self.buttonClose.setEnabled(False)

    def set_progressbar(self, count):
        """Slot for import thread rowcount signal"""
        self.progresscount = count / 100
        self.progresscount = int(self.progresscount)

    def threaddone(self):
        """Slot for import thread finished signal"""
        self.buttonStart.setEnabled(True)
        self.buttonClose.setEnabled(True)
        self.progress_bar.setValue(100)
        self.comm.done.emit()
