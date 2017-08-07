#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt5.QtWidgets import QDialog, QMessageBox

from resources import settings_dialog_rc as settingsui
from util import utils


class SettingsDialog(QDialog, settingsui.Ui_SettingsDialog):
    """
    Dialog for entering and updating current
    """

    def __init__(self, settings, parent=None):
        """Initialize the dialog"""
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)  # setup ui from resource file
        self.work = settings.current

        # assign values to input fields
        self.editUserMail.setText(self.work["usermail"])
        self.editUserPass.setText(self.work["userpass"])
        self.editUserCountry.setText(self.work["usercountry"])
        self.editHttp.setText(self.work["http"])
        self.editSmtp.setText(self.work["smtp"])
        self.editPort.setText(str(self.work["port"]))
        self.editMailTo.setText(self.work["mailto"])
        self.checkServerData.setChecked(utils.int2bool(self.work["sc"]))
        self.editMailServer.setText(self.work["mailserver"])
        self.editMailPort.setText(str(self.work["mailport"]))
        self.editMailUser.setText(self.work["mailuser"])
        self.editMailPass.setText(self.work["mailpass"])
        # connect to signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def accept(self):
        """User buttonbox_accepted_action current"""
        # assign input fields to current
        self.work["usermail"] = self.editUserMail.text().lower()
        self.work["userpass"] = self.editUserPass.text()
        self.work["usercountry"] = self.editUserCountry.text().lower()
        self.work["http"] = self.editHttp.text().lower()
        self.work["smtp"] = self.editSmtp.text().lower()
        self.work["port"] = self.editPort.text()
        self.work["mailto"] = self.editMailTo.text().lower()
        self.work["sc"] = utils.bool2int(self.checkServerData.isChecked())
        self.work["mailserver"] = self.editMailServer.text().lower()
        self.work["mailport"] = self.editMailPort.text()
        self.work["mailuser"] = self.editMailUser.text()
        self.work["mailpass"] = self.editMailPass.text()
        # check validity of vital current
        checkok = True
        items = []
        if self.work["usermail"] == "":
            items.append("Bruger email (fane 1)")
            checkok = False
        if self.work["userpass"] == "":
            items.append("Bruger kode (fane 1)")
            checkok = False
        if self.work["usercountry"] == "":
            items.append("Bruger land (fane 1)")
            checkok = False
        if self.work["smtp"] == "":
            items.append("SMTP server (fane 2)")
            checkok = False
        if self.work["port"] == "":
            items.append("SMTP port (fane 2)")
            checkok = False
        if self.work["mailto"] == "":
            items.append("Ordremodtager (fane 2)")
            checkok = False
        if self.work["http"] == "":
            items.append("Web server (fane 2)")
            checkok = False
        # inform user about current validity
        if not checkok:
            msgbox = QMessageBox()
            msgbox.warning(self,
                           self.tr("Eordre"),
                           self.tr("Der er mangler i dine indstillinger!\n{}".format("\n".join(items))),
                           QMessageBox.Ok)
            return False

        self.done(True)

    def reject(self):
        """User cancel dialog"""
        self.done(False)
