#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog

from util.worker import Worker
from util.status_communication import StatusCommunication
from resources.get_products_http_dialog_rc import Ui_getProductsHttpDialog


class GetProductsHttpDialog(QDialog, Ui_getProductsHttpDialog):
    """
    Dialog for importing products from server
    """
    sig_done = pyqtSignal()

    def __init__(self, app, products, settings, parent=None):
        """
        Initialize Dialog
        Args:
            products: main product object
            settings: main current object
        """
        super(GetProductsHttpDialog, self).__init__(parent)
        self.setupUi(self)
        self.__app = app
        self.progresscount = 1  # Used when setting progress values
        self.counter = 0  # Used when setting progress values
        self.rowcounter = 0  # Used when updating the status listbox
        # connect signals
        self.buttonStart.clicked.connect(self.button_start_clicked)
        self.buttonClose.clicked.connect(self.button_close_clicked)

    def add_row(self, text):
        """Slot for import thread processing signal"""
        self.log.append(text)

    @pyqtSlot()
    def button_close_clicked(self):
        """Slot for buttonClose clicked signal"""
        self.done(True)

    @pyqtSlot()
    def button_start_clicked(self):
        """Slot for buttonStart clicked signal"""
        # self.progress_bar.setValue(0)
        # # connect to the thread signals
        # self.thread.comm.processing.connect(self.add_row)
        # self.thread.comm.finished.connect(self.threaddone)
        # self.thread.comm.rowcount.connect(self.set_progressbar)
        # # start the thread
        # self.thread.start()
        # # we don't want to double the processes or close before finished
        # self.buttonStart.setEnabled(False)
        # self.buttonClose.setEnabled(False)

    @pyqtSlot()
    def threaddone(self):
        """Slot for import thread finished signal"""
        self.buttonStart.setEnabled(True)
        self.buttonClose.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.sig_done.emit()
