# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_report_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CreateReportDialog(object):
    def setupUi(self, CreateReportDialog):
        CreateReportDialog.setObjectName("CreateReportDialog")
        CreateReportDialog.resize(383, 94)
        self.buttonBox = QtWidgets.QDialogButtonBox(CreateReportDialog)
        self.buttonBox.setGeometry(QtCore.QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayoutWidget = QtWidgets.QWidget(CreateReportDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 271, 61))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit.setInputMask("")
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(CreateReportDialog)
        self.buttonBox.accepted.connect(CreateReportDialog.buttonbox_accepted_action)
        self.buttonBox.rejected.connect(CreateReportDialog.buttonbox_rejected_action)
        QtCore.QMetaObject.connectSlotsByName(CreateReportDialog)

    def retranslateUi(self, CreateReportDialog):
        _translate = QtCore.QCoreApplication.translate
        CreateReportDialog.setWindowTitle(_translate("CreateReportDialog", "Eordre"))
        self.lineEdit.setPlaceholderText(_translate("CreateReportDialog", "2017-12-31"))
        self.label.setText(_translate("CreateReportDialog", "Arbejdsdato (åååå-mm-dd)"))

