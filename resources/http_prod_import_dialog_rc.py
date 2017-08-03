# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'http_prod_import_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HttpProdImportDialog(object):
    """
    """
    def setupUi(self, HttpProdImportDialog):
        """

        Args:
            HttpProdImportDialog:
        """
        HttpProdImportDialog.setObjectName("HttpProdImportDialog")
        HttpProdImportDialog.resize(540, 113)
        self.itemList = QtWidgets.QListWidget(HttpProdImportDialog)
        self.itemList.setGeometry(QtCore.QRect(10, 10, 351, 60))
        self.itemList.setObjectName("itemList")
        self.progress_bar = QtWidgets.QProgressBar(HttpProdImportDialog)
        self.progress_bar.setGeometry(QtCore.QRect(10, 80, 521, 23))
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.buttonStart = QtWidgets.QPushButton(HttpProdImportDialog)
        self.buttonStart.setGeometry(QtCore.QRect(370, 10, 161, 26))
        self.buttonStart.setObjectName("buttonStart")
        self.buttonClose = QtWidgets.QPushButton(HttpProdImportDialog)
        self.buttonClose.setGeometry(QtCore.QRect(370, 40, 161, 26))
        self.buttonClose.setObjectName("buttonClose")

        self.retranslateUi(HttpProdImportDialog)
        QtCore.QMetaObject.connectSlotsByName(HttpProdImportDialog)

    def retranslateUi(self, HttpProdImportDialog):
        """

        Args:
            HttpProdImportDialog:
        """
        _translate = QtCore.QCoreApplication.translate
        HttpProdImportDialog.setWindowTitle(_translate("HttpProdImportDialog", "Prisliste import fra server"))
        self.buttonStart.setText(_translate("HttpProdImportDialog", "Start"))
        self.buttonClose.setText(_translate("HttpProdImportDialog", "Luk"))

