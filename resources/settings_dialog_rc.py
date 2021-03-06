# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_settingsDialog(object):
    def setupUi(self, settingsDialog):
        settingsDialog.setObjectName("settingsDialog")
        settingsDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        settingsDialog.resize(510, 281)
        settingsDialog.setMinimumSize(QtCore.QSize(0, 0))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/current/preferences-system-network.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        settingsDialog.setWindowIcon(icon)
        settingsDialog.setWindowOpacity(1.0)
        settingsDialog.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(settingsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 230, 481, 41))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.settingsStack = QtWidgets.QTabWidget(settingsDialog)
        self.settingsStack.setGeometry(QtCore.QRect(10, 10, 491, 211))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settingsStack.sizePolicy().hasHeightForWidth())
        self.settingsStack.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.settingsStack.setFont(font)
        self.settingsStack.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.settingsStack.setAutoFillBackground(False)
        self.settingsStack.setStyleSheet("")
        self.settingsStack.setIconSize(QtCore.QSize(16, 16))
        self.settingsStack.setElideMode(QtCore.Qt.ElideMiddle)
        self.settingsStack.setObjectName("settingsStack")
        self.settingsUser = QtWidgets.QWidget()
        self.settingsUser.setObjectName("settingsUser")
        self.editUserMail = QtWidgets.QLineEdit(self.settingsUser)
        self.editUserMail.setGeometry(QtCore.QRect(20, 20, 441, 28))
        self.editUserMail.setText("")
        self.editUserMail.setMaxLength(100)
        self.editUserMail.setFrame(True)
        self.editUserMail.setObjectName("editUserMail")
        self.editUserPass = QtWidgets.QLineEdit(self.settingsUser)
        self.editUserPass.setGeometry(QtCore.QRect(20, 60, 441, 28))
        self.editUserPass.setInputMask("")
        self.editUserPass.setMaxLength(100)
        self.editUserPass.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.editUserPass.setObjectName("editUserPass")
        self.editUserCountry = QtWidgets.QLineEdit(self.settingsUser)
        self.editUserCountry.setGeometry(QtCore.QRect(20, 100, 441, 26))
        self.editUserCountry.setMaxLength(2)
        self.editUserCountry.setObjectName("editUserCountry")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/system/credentials.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsStack.addTab(self.settingsUser, icon1, "")
        self.settingsStackPage2 = QtWidgets.QWidget()
        self.settingsStackPage2.setObjectName("settingsStackPage2")
        self.editHttp = QtWidgets.QLineEdit(self.settingsStackPage2)
        self.editHttp.setGeometry(QtCore.QRect(20, 100, 440, 28))
        self.editHttp.setMaxLength(100)
        self.editHttp.setObjectName("editHttp")
        self.editSmtp = QtWidgets.QLineEdit(self.settingsStackPage2)
        self.editSmtp.setGeometry(QtCore.QRect(20, 20, 281, 28))
        self.editSmtp.setText("")
        self.editSmtp.setMaxLength(100)
        self.editSmtp.setObjectName("editSmtp")
        self.editMailTo = QtWidgets.QLineEdit(self.settingsStackPage2)
        self.editMailTo.setGeometry(QtCore.QRect(20, 60, 441, 28))
        self.editMailTo.setText("")
        self.editMailTo.setMaxLength(100)
        self.editMailTo.setObjectName("editMailTo")
        self.editPort = QtWidgets.QLineEdit(self.settingsStackPage2)
        self.editPort.setGeometry(QtCore.QRect(310, 20, 151, 28))
        self.editPort.setMaxLength(3)
        self.editPort.setObjectName("editPort")
        self.checkServerData = QtWidgets.QCheckBox(self.settingsStackPage2)
        self.checkServerData.setGeometry(QtCore.QRect(20, 140, 431, 22))
        self.checkServerData.setObjectName("checkServerData")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/system/data-security.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsStack.addTab(self.settingsStackPage2, icon2, "")
        self.settingsStackPage3 = QtWidgets.QWidget()
        self.settingsStackPage3.setObjectName("settingsStackPage3")
        self.editMailServer = QtWidgets.QLineEdit(self.settingsStackPage3)
        self.editMailServer.setGeometry(QtCore.QRect(20, 20, 280, 28))
        self.editMailServer.setMaxLength(100)
        self.editMailServer.setObjectName("editMailServer")
        self.editMailPort = QtWidgets.QLineEdit(self.settingsStackPage3)
        self.editMailPort.setGeometry(QtCore.QRect(310, 20, 150, 28))
        self.editMailPort.setMaxLength(3)
        self.editMailPort.setObjectName("editMailPort")
        self.editMailUser = QtWidgets.QLineEdit(self.settingsStackPage3)
        self.editMailUser.setGeometry(QtCore.QRect(20, 60, 441, 28))
        self.editMailUser.setInputMask("")
        self.editMailUser.setText("")
        self.editMailUser.setMaxLength(100)
        self.editMailUser.setObjectName("editMailUser")
        self.editMailPass = QtWidgets.QLineEdit(self.settingsStackPage3)
        self.editMailPass.setGeometry(QtCore.QRect(20, 100, 441, 28))
        self.editMailPass.setText("")
        self.editMailPass.setMaxLength(100)
        self.editMailPass.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.editMailPass.setObjectName("editMailPass")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/system/mailbox.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsStack.addTab(self.settingsStackPage3, icon3, "")

        self.retranslateUi(settingsDialog)
        self.settingsStack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)
        settingsDialog.setTabOrder(self.settingsStack, self.editUserMail)
        settingsDialog.setTabOrder(self.editUserMail, self.editUserPass)
        settingsDialog.setTabOrder(self.editUserPass, self.editUserCountry)
        settingsDialog.setTabOrder(self.editUserCountry, self.editSmtp)
        settingsDialog.setTabOrder(self.editSmtp, self.editPort)
        settingsDialog.setTabOrder(self.editPort, self.editMailTo)
        settingsDialog.setTabOrder(self.editMailTo, self.editHttp)
        settingsDialog.setTabOrder(self.editHttp, self.editMailServer)
        settingsDialog.setTabOrder(self.editMailServer, self.editMailPort)
        settingsDialog.setTabOrder(self.editMailPort, self.editMailUser)
        settingsDialog.setTabOrder(self.editMailUser, self.editMailPass)

    def retranslateUi(self, settingsDialog):
        _translate = QtCore.QCoreApplication.translate
        settingsDialog.setWindowTitle(_translate("settingsDialog", "Indstillinger"))
        self.editUserMail.setPlaceholderText(_translate("settingsDialog", "brugers mail adresse: email@domæne.tld"))
        self.editUserPass.setPlaceholderText(_translate("settingsDialog", "din adgangs frase"))
        self.editUserCountry.setPlaceholderText(_translate("settingsDialog", "landkode: dk"))
        self.settingsStack.setTabText(self.settingsStack.indexOf(self.settingsUser), _translate("settingsDialog", "Bruger"))
        self.editHttp.setPlaceholderText(_translate("settingsDialog", "webserver: http://localhost:8080"))
        self.editSmtp.setPlaceholderText(_translate("settingsDialog", "post server: mail.domain.tld"))
        self.editMailTo.setPlaceholderText(_translate("settingsDialog", "modtager email: email@domain.tld"))
        self.editPort.setPlaceholderText(_translate("settingsDialog", "port: 25"))
        self.checkServerData.setText(_translate("settingsDialog", "Ved programstart kontroller server data"))
        self.settingsStack.setTabText(self.settingsStack.indexOf(self.settingsStackPage2), _translate("settingsDialog", "Data"))
        self.editMailServer.setPlaceholderText(_translate("settingsDialog", "post server: server.domain.tld"))
        self.editMailPort.setPlaceholderText(_translate("settingsDialog", "port: 25"))
        self.editMailUser.setPlaceholderText(_translate("settingsDialog", "post server: brugernavn"))
        self.editMailPass.setPlaceholderText(_translate("settingsDialog", "post server: adgangskode"))
        self.settingsStack.setTabText(self.settingsStack.indexOf(self.settingsStackPage3), _translate("settingsDialog", "E-post"))

from . import system_rc
