#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QDialog

from util.worker import Worker
from resources.get_customers_http_dialog_rc import Ui_getCustomersHttpDialog


class GetCustomersHttpDialog(QDialog, Ui_getCustomersHttpDialog):
    """
    Import customers from http
    """

    sig_done = pyqtSignal()

    def __init__(self, app, customers, employees, settings):
        """
        Initialize Dialog
        Args:
            customers: main current object
            employees: main employeeid object
            settings: main current object
        """
        super(GetCustomersHttpDialog, self).__init__()
        self.setupUi(self)
        self.__app = app

        self.counter = 0  # Used when setting progress values
        self.rowcounter = 0  # Used when updating the status listbox
        self.progresscount = 0
        # connect signals
        self.buttonStart.clicked.connect(self.button_start_action)
        self.buttonClose.clicked.connect(self.button_close_action)

    def add_row(self, text):
        """Slot for import thread processing signal"""
        self.log.append(text)

    def button_close_action(self):
        """Slot for buttonClose clicked signal"""
        self.done(True)

    def button_start_action(self):
        """Slot for buttonStart clicked signal"""
        self.progress_bar.setValue(0, 0)
        # # connect to the thread signals
        # self.thread.comm.done.connect(self.threaddone)
        # self.thread.comm.status.connect(self.add_row)
        # # start the thread
        # self.thread.start()
        # # we don't want to double the processes or close before finished
        # self.buttonStart.setEnabled(False)
        # self.buttonClose.setEnabled(False)

    def threaddone(self):
        """Slot for import thread finished signal"""
        self.buttonStart.setEnabled(True)
        self.buttonClose.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.sig_done.emit()
