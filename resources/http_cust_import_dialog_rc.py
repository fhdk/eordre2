# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'http_cust_import_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HttpCustImportDialog(object):
    """
    """
    def setupUi(self, HttpCustImportDialog):
        """

        Args:
            HttpCustImportDialog:
        """
        HttpCustImportDialog.setObjectName("HttpCustImportDialog")
        HttpCustImportDialog.resize(540, 109)
        self.itemList = QtWidgets.QListWidget(HttpCustImportDialog)
        self.itemList.setGeometry(QtCore.QRect(10, 10, 351, 60))
        self.itemList.setObjectName("itemList")
        self.progress_bar = QtWidgets.QProgressBar(HttpCustImportDialog)
        self.progress_bar.setGeometry(QtCore.QRect(10, 80, 521, 23))
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.buttonStart = QtWidgets.QPushButton(HttpCustImportDialog)
        self.buttonStart.setGeometry(QtCore.QRect(370, 10, 161, 26))
        self.buttonStart.setObjectName("buttonStart")
        self.buttonClose = QtWidgets.QPushButton(HttpCustImportDialog)
        self.buttonClose.setGeometry(QtCore.QRect(370, 40, 161, 26))
        self.buttonClose.setObjectName("buttonClose")

        self.retranslateUi(HttpCustImportDialog)
        QtCore.QMetaObject.connectSlotsByName(HttpCustImportDialog)

    def retranslateUi(self, HttpCustImportDialog):
        """

        Args:
            HttpCustImportDialog:
        """
        _translate = QtCore.QCoreApplication.translate
        HttpCustImportDialog.setWindowTitle(_translate("HttpCustImportDialog", "Kunde import fra server"))
        self.buttonStart.setText(_translate("HttpCustImportDialog", "Start"))
        self.buttonClose.setText(_translate("HttpCustImportDialog", "Luk"))

