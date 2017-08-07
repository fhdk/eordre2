#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog

from resources.get_customers_http_dialog_rc import Ui_getCustomersHttpDialog
from util import threads


class Communicate(QObject):
    """
    Broadcasting signals
    """
    finished = pyqtSignal()


class GetCustomersHttpDialog(QDialog, Ui_getCustomersHttpDialog):
    """
    """
    def __init__(self, customers, employees, settings, parent=None):
        """
        Initialize Dialog
        Args:
            customers: main current object
            employees: main employeeid object
            settings: main current object
        """
        super(GetCustomersHttpDialog, self).__init__(parent)
        self.setupUi(self)

        self.c = Communicate()

        self.counter = 0  # Used when setting progress values
        self.rowcounter = 0  # Used when updating the status listbox
        self.progresscount = 0
        self.import_thread = threads.ImportCustomersThread(customers=customers,
                                                           employees=employees,
                                                           settings=settings)
        # connect signals
        self.buttonStart.clicked.connect(self.button_start_action)
        self.buttonClose.clicked.connect(self.button_close_action)

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

    def button_close_action(self):
        """Slot for buttonClose clicked signal"""
        self.done(True)

    def button_start_action(self):
        """Slot for buttonStart clicked signal"""
        self.progress_bar.setValue(0)
        # connect to the thread signals
        self.import_thread.c.finished.connect(self.threaddone)
        self.import_thread.c.processing.connect(self.add_row)
        self.import_thread.c.rowcount.connect(self.set_progressbar)
        # start the thread
        self.import_thread.start()
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
        self.c.finished.emit()
