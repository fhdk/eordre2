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
    Dialog for entering and updating settings
    """

    def __init__(self, settings, parent=None):
        """Initialize the dialog"""
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)  # setup ui from resource file
        self.app_settings = settings  # assign settings object
        # assign values to input fields
        self.editUserMail.setText(settings["usermail"])
        self.editUserPass.setText(settings["userpass"])
        self.editUserCountry.setText(settings["usercountry"])
        self.editHttp.setText(settings["http"])
        self.editSmtp.setText(settings["smtp"])
        self.editPort.setText(str(settings["port"]))
        self.editMailTo.setText(settings["mailto"])
        self.checkServerData.setChecked(utils.int2bool(settings["sc"]))
        self.editMailServer.setText(settings["mailserver"])
        self.editMailPort.setText(str(settings["mailport"]))
        self.editMailUser.setText(settings["mailuser"])
        self.editMailPass.setText(settings["mailpass"])
        # connect to signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def accept(self):
        """User buttonbox_accepted_action settings"""
        # assign input fields to settings
        self.app_settings["usermail"] = self.editUserMail.text().lower()
        self.app_settings["userpass"] = self.editUserPass.text()
        self.app_settings["usercountry"] = self.editUserCountry.text().lower()
        self.app_settings["http"] = self.editHttp.text().lower()
        self.app_settings["smtp"] = self.editSmtp.text().lower()
        self.app_settings["port"] = self.editPort.text()
        self.app_settings["mailto"] = self.editMailTo.text().lower()
        self.app_settings["sc"] = utils.bool2int(self.checkServerData.isChecked())
        self.app_settings["mailserver"] = self.editMailServer.text().lower()
        self.app_settings["mailport"] = self.editMailPort.text()
        self.app_settings["mailuser"] = self.editMailUser.text()
        self.app_settings["mailpass"] = self.editMailPass.text()
        # check validity of vital settings
        check = self.app_settings
        checkok = True
        items = []
        if check["usermail"] == "":
            items.append("Bruger email (fane 1)")
            checkok = False
        if check["userpass"] == "":
            items.append("Bruger kode (fane 1)")
            checkok = False
        if check["usercountry"] == "":
            items.append("Bruger land (fane 1)")
            checkok = False
        if check["smtp"] == "":
            items.append("SMTP server (fane 2)")
            checkok = False
        if check["port"] == "":
            items.append("SMTP port (fane 2)")
            checkok = False
        if check["mailto"] == "":
            items.append("Ordremodtager (fane 2)")
            checkok = False
        if check["http"] == "":
            items.append("Web server (fane 2)")
            checkok = False
        # inform user about settings validity
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
