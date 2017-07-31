# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_import_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FileImportDialog(object):
    def setupUi(self, FileImportDialog):
        FileImportDialog.setObjectName("FileImportDialog")
        FileImportDialog.resize(615, 278)
        FileImportDialog.setModal(True)
        self.comboImport = QtWidgets.QComboBox(FileImportDialog)
        self.comboImport.setGeometry(QtCore.QRect(140, 10, 210, 40))
        self.comboImport.setObjectName("comboImport")
        self.buttonBrowse = QtWidgets.QPushButton(FileImportDialog)
        self.buttonBrowse.setGeometry(QtCore.QRect(370, 10, 229, 40))
        self.buttonBrowse.setAutoDefault(False)
        self.buttonBrowse.setObjectName("buttonBrowse")
        self.buttonImport = QtWidgets.QPushButton(FileImportDialog)
        self.buttonImport.setGeometry(QtCore.QRect(370, 50, 229, 40))
        self.buttonImport.setObjectName("buttonImport")
        self.label = QtWidgets.QLabel(FileImportDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 121, 40))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.buttonClose = QtWidgets.QPushButton(FileImportDialog)
        self.buttonClose.setGeometry(QtCore.QRect(370, 230, 230, 40))
        self.buttonClose.setObjectName("buttonClose")
        self.listImported = QtWidgets.QListWidget(FileImportDialog)
        self.listImported.setEnabled(True)
        self.listImported.setGeometry(QtCore.QRect(9, 91, 341, 180))
        self.listImported.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listImported.setObjectName("listImported")
        self.txtSelectedFile = QtWidgets.QLineEdit(FileImportDialog)
        self.txtSelectedFile.setEnabled(True)
        self.txtSelectedFile.setGeometry(QtCore.QRect(10, 50, 341, 41))
        self.txtSelectedFile.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.txtSelectedFile.setObjectName("txtSelectedFile")
        self.checkHeaders = QtWidgets.QCheckBox(FileImportDialog)
        self.checkHeaders.setGeometry(QtCore.QRect(370, 100, 220, 24))
        self.checkHeaders.setChecked(True)
        self.checkHeaders.setObjectName("checkHeaders")

        self.retranslateUi(FileImportDialog)
        QtCore.QMetaObject.connectSlotsByName(FileImportDialog)
        FileImportDialog.setTabOrder(self.comboImport, self.buttonBrowse)
        FileImportDialog.setTabOrder(self.buttonBrowse, self.checkHeaders)
        FileImportDialog.setTabOrder(self.checkHeaders, self.buttonImport)
        FileImportDialog.setTabOrder(self.buttonImport, self.buttonClose)
        FileImportDialog.setTabOrder(self.buttonClose, self.txtSelectedFile)
        FileImportDialog.setTabOrder(self.txtSelectedFile, self.listImported)

    def retranslateUi(self, FileImportDialog):
        _translate = QtCore.QCoreApplication.translate
        FileImportDialog.setWindowTitle(_translate("FileImportDialog", "Data import"))
        self.buttonBrowse.setText(_translate("FileImportDialog", "Find import fil ..."))
        self.buttonImport.setText(_translate("FileImportDialog", "Import"))
        self.label.setText(_translate("FileImportDialog", "Import"))
        self.buttonClose.setText(_translate("FileImportDialog", "Luk"))
        self.checkHeaders.setText(_translate("FileImportDialog", "Første linje er feltnavne"))

