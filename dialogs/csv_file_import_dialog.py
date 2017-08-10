#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from configuration import config
from resources.csv_file_import_dialog_rc import Ui_csvFileImportDialog


class CsvImportComm(QObject):
    """
    Broadcast signals
    """
    customersdone = pyqtSignal()


class CsvFileImportDialog(QDialog, Ui_csvFileImportDialog):
    """
    Dialog for importing CSV data
    """

    def __init__(self, contacts, customers, details, employees, reports, visits, tables, parent=None):
        """Initialize Dialog"""
        super(CsvFileImportDialog, self).__init__(parent)
        self.setupUi(self)

        self.contacts = contacts
        self.customers = customers
        self.employees = employees
        self.visits = visits
        self.details = details
        self.reports = reports

        self.c = CsvImportComm()
        self.file_dialog = QFileDialog()

        self.buttonImport.enabled = False
        # connect to signals
        self.comboImport.currentIndexChanged.connect(self.combo_current_index_changed_action)
        self.buttonBrowse.clicked.connect(self.button_browse_action)
        self.buttonImport.clicked.connect(self.button_import_action)
        self.buttonClose.clicked.connect(self.button_close_action)
        # Setup which tables can be imported
        for item in tables:
            self.comboImport.addItem(item[0], item[1])
            self.comboImport.setCurrentIndex(0)
        self.browseDir = config.HOME  # setup file import dir to home
        self.selectedFile = ""  # initalize selected file
        self.selectedTable = self.comboImport.itemData(0)  # initialize selected table

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
        self.done(False)

    def button_import_action(self):
        """Slot for buttonImport clicked signal"""
        # we dont want buttons to be activated twice during import
        self.buttonImport.enabled = False
        self.buttonBrowse.enabled = False
        self.buttonClose.enabled = False

        if self.selectedFile:
            # notice to init_new_detail to list box
            notice = self.comboImport.currentText() + " er importeret."
            success = False
            # import selected file to contact table
            if self.selectedTable == "contact":
                success = self.contacts.import_csv(self.selectedFile,
                                                   self.checkHeaders.isChecked())

            # import selected file to current table
            if self.selectedTable == "customer":
                success = self.customers.import_csv(self.selectedFile,
                                                    self.checkHeaders.isChecked())
                self.c.customersdone.emit()

            # import selected file to ordervisit table
            if self.selectedTable == "visit":
                success = self.visits.import_csv(self.selectedFile,
                                                 self.checkHeaders.isChecked())

            # import selected file to orderline table
            if self.selectedTable == "detail":
                success = self.details.import_csv(self.selectedFile,
                                                  self.checkHeaders.isChecked())

            # import selected file to reportid table
            if self.selectedTable == "report":
                success = self.reports.import_csv(self.selectedFile,
                                                  self.employees.current["employee_id"],
                                                  self.checkHeaders.isChecked())

            if success:
                self.listImported.addItem(notice)
            else:
                QMessageBox.information(self, "Doh!", "Der er opstået en fejl!", QMessageBox.Ok)
                return

            self.selectedFile = ""
            self.txtSelectedFile.clear()
            self.comboImport.removeItem(self.comboImport.currentIndex())
            self.comboImport.setCurrentIndex(0)

        self.buttonImport.enabled = False  # disable the button till next file is selected
        self.buttonBrowse.enabled = True  # enable browse button
        self.buttonClose.enabled = True  # enable close button

    def combo_current_index_changed_action(self):
        """Slot for ComboBox currentIndexChanged signal"""
        self.selectedTable = self.comboImport.itemData(self.comboImport.currentIndex())
