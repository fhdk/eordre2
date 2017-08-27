#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog

from util.worker import Worker
from resources.get_products_http_dialog_rc import Ui_getProductsHttpDialog

B_COLOR = "\033[0;37m"
E_COLOR = "\033[0;m"
DBG = True

__module__ = "products_http"


def printit(string):
    """Print a variable string for debug purposes"""
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


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
        self.products = products
        self.settings = settings
        # connect signals
        self.buttonStart.clicked.connect(self.button_start_clicked)
        self.buttonClose.clicked.connect(self.button_close_clicked)

        self.__workers_done = 0
        self.__threads = []

    @pyqtSlot(int, str)
    def on_status(self, worker_id: int, text: str):
        """Slot for import thread processing signal"""
        status = "{}-{}".format(worker_id, text)
        self.log.append(status)

    @pyqtSlot()
    def button_close_clicked(self):
        """Slot for buttonClose clicked signal"""
        self.done(True)

    @pyqtSlot()
    def button_start_clicked(self):
        """Slot for buttonStart clicked signal"""
        self.progressBar.setRange(0, 0)
        self.buttonStart.setEnabled(False)
        self.buttonClose.setEnabled(False)
        worker = Worker(20, self.__app)
        thread = QThread(self)
        thread.setObjectName("products_http")
        self.__threads.append((thread, worker))
        worker.moveToThread(thread)
        worker.sig_step.connect(self.on_worker_step)
        worker.status.connect(self.on_status)
        worker.done.connect(self.on_done)
        worker.sig_done.connect(self.on_worker_done)
        try:
            thread.started.connect(worker.import_products_http(self.products, self.settings))
            thread.start()
        except TypeError as t:
            if DBG:
                printit(" ->products -> http\n ->exception handled: {}".format(t))

    @pyqtSlot()
    def on_done(self):
        """Slot for import thread finished signal"""
        self.buttonStart.setEnabled(True)
        self.buttonClose.setEnabled(True)
        self.progressBar.setRange(0, 1)
        self.sig_done.emit()

    @pyqtSlot(int, str)
    def on_worker_step(self, worker_id: int, data: str):
        self.log.append('Worker #{}: {}'.format(worker_id, data))
        self.progress.append('{}: {}'.format(worker_id, data))

    @pyqtSlot(int)
    def on_worker_done(self, worker_id: int):
        self.log.append('worker #{} done'.format(worker_id))
        self.progress.append('-- Worker {} DONE'.format(worker_id))
        self.__workers_done += 1
        if self.__workers_done == len(self.__threads):
            self.progressBar.setRange(0, 1)  # set progressbar normal
            self.log.append('No more workers active')
            self.sig_done.emit()
            # self.button_start_threads.setEnabled(True)
            # self.button_stop_threads.setDisabled(True)
            # self.__threads = None
