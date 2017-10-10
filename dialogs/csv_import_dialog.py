#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# Copyright: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from configuration import config
from resources.csv_import_dialog_rc import Ui_csvFileImportDialog
from util.worker import Worker

B_COLOR = "\033[0;37m"
E_COLOR = "\033[0;m"
DBG = True

__module__ = "report"


def printit(string):
    """Print a variable string for debug purposes"""
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class CsvFileImportDialog(QDialog, Ui_csvFileImportDialog, QObject):
    """
    Dialog for importing CSV data
    """
    sig_done = pyqtSignal()

    def __init__(self, app, contact, customer, detail, employee, report, visit, tables):
        """Initialize Dialog"""
        super(CsvFileImportDialog, self).__init__()
        self.setupUi(self)
        self.__app = app
        self.contacts = contact
        self.customers = customer
        self.details = detail
        self.employees = employee
        self.reports = report
        self.visits = visit

        self.file_dialog = QFileDialog()
        self.progressBar.setRange(0, 1)

        self.buttonImport.setEnabled(False)
        # connect to signals
        self.comboImport.currentIndexChanged.connect(self.combo_changed_action)
        self.buttonBrowse.clicked.connect(self.button_browse_action)
        self.buttonImport.clicked.connect(self.button_import_action)
        self.buttonClose.clicked.connect(self.button_close_action)
        self.txtSelectedFile.textChanged.connect(self.on_selected_file_changed)
        # Setup which tables can be imported
        for item in tables:
            self.comboImport.addItem(item[0], item[1])
            self.comboImport.setCurrentIndex(0)
        self.browseDir = config.HOME  # setup file import dir to home
        self.selectedFile = ""  # initalize selected file
        self.selectedTable = self.comboImport.itemData(0)  # initialize selected table

        self.__workers_done = 0
        self.__threads = []

    def button_browse_action(self):
        """Slot for buttonBrowse clicked signal"""
        # browse for import file
        data = self.file_dialog.getOpenFileName(self,
                                                "Vælg import fil",
                                                self.browseDir,
                                                "Text files (*.csv)")
        self.selectedFile = data[0]
        self.browseDir = os.path.dirname(data[0])
        self.txtSelectedFile.setText(self.selectedFile)

    def button_close_action(self):
        """Slot for buttonClose clicked signal"""
        if not self.__workers_done == 5:
            self.sig_done.emit()
        self.done(False)

    def button_import_action(self):
        """
        Slot for buttonImport clicked signal
        """
        self.buttonClose.setEnabled(False)
        headers = True
        if not self.checkHeaders.isChecked():
            headers = False
        if DBG:
            printit(" ->headers: {}\n"
                    " ->contacts.contact_list: {}\n"
                    " ->customers.customer_list: {}\n"
                    " ->details.details_list: {}\n"
                    " ->reports.report_list: {}\n"
                    " ->visits.visit_list_customer: {}\n".format(headers,
                                                                 self.contacts.contact_list,
                                                                 self.customers.customer_list,
                                                                 self.details.details_list,
                                                                 self.reports.report_list,
                                                                 self.visits.visit_list_customer))
        self.progressBar.setRange(0, 0)  # set spinning progressbar

        if self.selectedFile:
            # import selected file to contact table
            if self.selectedTable == "contact":
                worker = Worker(1, self.__app)
                thread = QThread(self)
                thread.setObjectName("contacts_csv")
                self.__threads.append((thread, worker))
                worker.moveToThread(thread)
                worker.sig_status.connect(self.on_status)
                worker.sig_done.connect(self.on_done)
                try:
                    thread.started.connect(worker.import_contacts_csv(self.contacts,
                                                                      self.selectedFile,
                                                                      header=headers))
                    thread.start()
                except TypeError as t:
                    if DBG:
                        printit(" ->contacts\n"
                                "  ->exception handled: {}".format(t))

            # import selected file to customer table
            if self.selectedTable == "customer":
                worker = Worker(2, self.__app)
                thread = QThread(self)
                thread.setObjectName("customers_csv")
                self.__threads.append((thread, worker))
                worker.moveToThread(thread)
                worker.sig_status.connect(self.on_status)
                worker.sig_done.connect(self.on_done)
                try:
                    thread.started.connect(worker.import_customers_csv(self.customers,
                                                                       self.selectedFile,
                                                                       header=headers))
                    thread.start()
                except TypeError as t:
                    if DBG:
                        printit(" ->customers\n"
                                "  ->exception handled: {}".format(t))

            # import selected file to visit table
            if self.selectedTable == "visit":
                worker = Worker(3, self.__app)
                thread = QThread(self)
                thread.setObjectName("visits_csv")
                self.__threads.append((thread, worker))
                worker.moveToThread(thread)
                worker.sig_status.connect(self.on_status)
                worker.sig_done.connect(self.on_done)
                try:
                    thread.started.connect(worker.import_visits_csv(self.visits,
                                                                    self.selectedFile,
                                                                    header=headers))
                    thread.start()
                except TypeError as t:
                    if DBG:
                        printit(" ->visits\n"
                                "  ->exception handled: {}".format(t))

            # import selected file to detail table
            if self.selectedTable == "detail":
                worker = Worker(4, self.__app)
                thread = QThread(self)
                thread.setObjectName("details_csv")
                self.__threads.append((thread, worker))
                worker.moveToThread(thread)
                worker.sig_status.connect(self.on_status)
                worker.sig_done.connect(self.on_done)
                try:
                    thread.started.connect(worker.import_visit_details_csv(self.details,
                                                                           self.selectedFile,
                                                                           header=headers))
                    thread.start()
                except TypeError as t:
                    if DBG:
                        printit(" ->visit_details\n"
                                "  ->exception handled: {}".format(t))

            # import selected file to report table
            if self.selectedTable == "report":
                worker = Worker(5, self.__app)
                thread = QThread(self)
                thread.setObjectName("reports_csv")
                self.__threads.append((thread, worker))
                worker.moveToThread(thread)
                worker.sig_status.connect(self.on_status)
                worker.sig_done.connect(self.on_done)
                try:
                    thread.started.connect(worker.import_reports_csv(self.employees.active["employee_id"],
                                                                     self.reports,
                                                                     self.selectedFile,
                                                                     header=headers))
                    thread.start()
                except TypeError as t:
                    if DBG:
                        printit(" ->reports\n"
                                "  ->exception handled: {}".format(t))

            self.selectedFile = ""
            self.txtSelectedFile.clear()
            self.comboImport.removeItem(self.comboImport.currentIndex())
            self.comboImport.setCurrentIndex(0)

        self.buttonImport.setEnabled(False)  # disable the button until next file is selected
        self.buttonBrowse.setEnabled(True)  # enable browse button
        self.buttonClose.setEnabled(True)  # enable close button

    @pyqtSlot()
    def combo_changed_action(self):
        """Slot for ComboBox currentIndexChanged signal"""
        self.selectedTable = self.comboImport.itemData(self.comboImport.currentIndex())

    @pyqtSlot(int)
    def on_done(self, worker_id: int):
        """
        Executes when the import is done
        """
        self.__workers_done += 1
        if self.__workers_done == 5:
            self.sig_done.emit()
            self.button_close_action()
        self.progressBar.setRange(0, 1)
        self.buttonImport.setEnabled(False)  # disable the button till next file is selected
        self.buttonBrowse.setEnabled(True)  # enable browse button
        self.buttonClose.setEnabled(True)  # enable close button

    @pyqtSlot(int, str)
    def on_status(self, worker_id: int, text: str):
        """
        Process status notification
        """
        self.log.append(text)
        if text.startswith("ERROR") or text.startswith("FEJL"):
            if DBG:
                printit(" ->text: {}".format(text))
            title = "Import fejl"
            QMessageBox.information(self, title, text, QMessageBox.Ok)

    @pyqtSlot()
    def on_selected_file_changed(self):
        self.selectedFile = self.txtSelectedFile.text()
        if self.selectedFile.endswith(".csv"):
            self.buttonImport.setEnabled(True)
        else:
            self.buttonImport.setEnabled(False)
        if DBG:
            printit(" ->selectedFile: {}".format(self.selectedFile))
