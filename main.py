#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Eordre application"""

import datetime
import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSplashScreen, QTreeWidgetItem

# import resources.splash_rc
import util.passwdfn
from configuration import configfn, config
from dialogs.create_order_dialog import CreateOrderDialog
from dialogs.create_report_dialog import CreateReportDialog
from dialogs.file_import_dialog import FileImportDialog
from dialogs.http_cust_import_dialog import HttpCustImportDialog
from dialogs.http_prod_import_dialog import HttpProdImportDialog
from dialogs.settings_dialog import SettingsDialog
from models import contact, customer, employee, visit, orderline, product, report, settings
from resources.main_window_rc import Ui_MainWindow
from util import httpfn, dbfn
from util.rules import check_settings

__appname__ = "Eordre NG"
__module__ = "main"


# noinspection PyMethodMayBeStatic
class MainWindow(QMainWindow, Ui_MainWindow):
    """Main Application Window"""

    def __init__(self):
        """Initialize MainWindow class"""
        super(MainWindow, self).__init__()
        self.setupUi(self)

        configfn.check_config_folder()  # Check app folder in users home
        dbfn.create_tables()  # Create the needed tables

        self.txtWorkdate.setText(datetime.date.today().isoformat())  # set workdate
        self.currentCustomer = {}  # Initialize an empty customer dict
        self.Contact = contact.Contact()  # Initialize Contact object
        self.Customer = customer.Customer()  # Initialize Customer object
        self.Employee = employee.Employee()  # Initialize Employee object
        self.OrderVisit = visit.Visit()  # Initialize OrderVisit object
        self.OrderLine = orderline.OrderLine()  # Initialize OrderLine object 
        self.Product = product.Product()  # Initialize Product object
        self.Report = report.Report()  # Initialize Report object
        self.Settings = settings.Setting()  # Initialize Settings object
        # connect signals
        self.actionExit.triggered.connect(self.exit_action)
        self.actionSettings.triggered.connect(self.settings_dialog_action)
        self.actionCsvFileImport.triggered.connect(self.file_import_action)
        self.actionHttpGetCatalog.triggered.connect(self.get_product_action)
        self.actionHttpGetCustomers.triggered.connect(self.get_customers_action)
        self.actionAboutQt.triggered.connect(self.about_qt_action)
        self.actionAboutSoftware.triggered.connect(self.about_software_action)
        self.actionShowContactData.triggered.connect(self.contact_data_action)
        self.actionShowMasterData.triggered.connect(self.master_data_action)
        self.actionShowOrderData.triggered.connect(self.order_data_action)
        self.actionShowVisitData.triggered.connect(self.visit_data_action)
        self.actionCreateCustomer.triggered.connect(self.create_customer_action)
        self.actionCreateOrder.triggered.connect(self.create_order_action)
        self.actionCreateReport.triggered.connect(self.create_report_action)
        self.actionUpdateCustomer.triggered.connect(self.update_customer_action)
        self.customerList.currentItemChanged.connect(self.current_cust_changed_action)
        self.actionZeroDatabase.triggered.connect(self.zero_database_action)

    def about_qt_action(self):
        """Slot for aboutQt triggered signal"""
        msgbox = QMessageBox()
        msgbox.aboutQt(self, "Eordre NG")

    def about_software_action(self):
        """Slot for aboutSoftware triggered signal"""
        msgbox = QMessageBox()
        msgbox.about(self, "Eordre NG",
                     "Bygget med Python 3.6 og Qt framework\n\nFrede Hundewadt (c) 2017")

    def app_run(self):
        """Setup database and basic configuration"""
        # Settings needs to be up for inet connection to work
        is_set = check_settings(self.Settings.current_settings)
        if is_set:
            try:
                _ = self.Employee.current_employee["fullname"]
            except KeyError:
                if httpfn.inet_conn_check():
                    e = httpfn.get_employee_data(self.Settings.current_settings)
                    if e:
                        e = [1] + e
                        self.Employee.insert_(e)
        else:
            msgbox = QMessageBox()
            msgbox.about(self,
                         "Eordre NG",
                         "Der er mangler i dine indstillinger.\n\nDisse skal tilpasses.")
            self.settings_dialog_action()

        self.populate_customer_list()

    def close_event(self, event):
        """Slot for close event signal
        intended use is warning about unsaved data
        """
        pass

    def contact_data_action(self):
        """Slot for contactData triggered signal"""
        self.customerInfoStack.setCurrentIndex(1)

    def create_customer_action(self):
        """Slot for createCustomer triggered signal"""
        if not self.txtNewCompany.text() or not self.txtNewPhone1.text():
            msgbox = QMessageBox()
            msgbox.information(self,
                               "Eordre NG",
                               "Snap - Jeg mangler:\n Firma navn \n Telefon nummer",
                               QMessageBox.Ok)
        else:
            msgbox = QMessageBox()
            msgbox.information(self,
                               "Eordre NG",
                               "Gem kunde til database\n\n" +
                               self.txtNewCompany.text() + "\n" +
                               self.txtNewPhone1.text(),
                               QMessageBox.Ok)

    def create_order_action(self):
        """Slot for createOrder triggered signal"""
        if not self.Report.load_report(self.txtWorkdate.text()):
            msgbox = QMessageBox()
            msgbox.information(self,
                               "Eordre NG",
                               "Der er ingen dagsrapport for idag!",
                               QMessageBox.Ok)
            return False

        if self.currentCustomer:
            order_dialog = CreateOrderDialog(self,
                                             self.Report.current_report,
                                             self.Customer.current_customer,
                                             self.Employee.current_employee)
            if order_dialog.exec_():

                pass
        else:
            msgbox = QMessageBox()
            msgbox.information(self,
                               "Eordre NG",
                               "Ingen kunder - ingen ordre!",
                               QMessageBox.Ok)

    def create_report_action(self):
        """Slot for createReport triggered signal"""
        try:
            repdate = self.Report.current_report["repdate"]
            if not repdate == self.txtWorkdate.text():
                infotext = "Den aktive rapportdato er\ndato: {}\narbejdsdato: {}".format(
                    repdate, self.txtWorkdate.text())
                msgbox = QMessageBox()
                msgbox.information(self, "Eordre NG", infotext, QMessageBox.Ok)

        except KeyError:
            create_report_dialog = CreateReportDialog(self.txtWorkdate.text())  # Create dialog
            if create_report_dialog.exec_():  # Execute dialog - show it
                self.txtWorkdate.setText(create_report_dialog.workdate)
                msgbox = QMessageBox()
                msgbox.information(self,
                                   "Eordre NG",
                                   "Der er oprettet dagsrapport for <strong>{}</strong>!".format(
                                       self.txtWorkdate.text()),
                                   QMessageBox.Ok)
                self.Report.create_(self.Employee.current_employee, self.txtWorkdate.text())

            else:
                msgbox = QMessageBox()
                msgbox.information(self,
                                   "Eordre NG",
                                   "Der er <strong>IKKE</strong> oprettet dagsrapport!",
                                   QMessageBox.Ok)

    def current_cust_changed_action(self, current, previous):
        """Slot for listbox current item changed signal
        propagate changes to currently selected customer
        to related customer info pages
        :param current: currently selected item
        :param previous: previous selected item
        """
        for found in self.Customer.customer_list:
            try:
                if found["company"] == current.text(0):
                    if found["account"] == current.text(1):
                        # set current customer
                        self.currentCustomer = found
                        # customer master data
                        self.txtAccount.setText(found["account"])
                        self.txtCompany.setText(found["company"])
                        self.txtAddress1.setText(found["address1"])
                        self.txtAddress2.setText(found["address2"])
                        self.txtZipCode.setText(found["zipcode"])
                        self.txtCityName.setText(found["city"])
                        self.txtPhone1.setText(found["phone1"])
                        self.txtPhone2.setText(found["phone2"])
                        self.txtEmail.setText(found["email"])
                        self.txtFactor.setText(str(found["factor"]))
                        self.txtInfoText.clear()
                        self.txtInfoText.insertPlainText(found["infotext"])
            except AttributeError:
                pass

    def data_export_action(self):
        """Slot for dataExport triggered signal"""
        msgbox = QMessageBox()
        msgbox.information(self,
                           "Eordre NG",
                           "Opret CSV data backup",
                           QMessageBox.Ok)

    def exit_action(self):
        """Slot for exit triggered signal"""
        self.close_event(self)
        app.quit()

    def file_import_action(self):
        """Slot for fileImport triggered signal"""
        if self.Customer.customer_list or self.Report.current_report:
            # Warn user that import deletes existing data
            msgbox = QMessageBox()
            msgbox.warning(self,
                           "Eordre NG",
                           "<strong>Ved import slettes alle eksisterende data</strong>!\n\n"
                           "Af hensyn til sammenkædning af data er det bedst,\n"
                           "at du importer alle tabeller der findes i dropned listen!",
                           QMessageBox.Ok)
        import_dialog = FileImportDialog(config.CSVDATA)  # Create import dialog

        if import_dialog.exec_():  # Execute the dialog - show it
            self.populate_customer_list()  # Reload the customer list
        else:
            pass

    def file_import_customer_done(self):
        """Slot for customer import done. Used to trigger populate_customer_list"""
        self.populate_customer_list()

    def get_customers_action(self):
        """Slot for getCustomers triggered signal"""
        import_customers = HttpCustImportDialog()  # Create dialog object
        import_customers.c.finished.connect(self.get_customers_finished)
        import_customers.exec_()  # Execute the dialog - show it

    def get_customers_finished(self):
        """Slot for getCustomers finished signal"""
        self.populate_customer_list()  # load_ customers

    def get_product_action(self):
        """Slot for getProducts triggered signal"""
        import_product = HttpProdImportDialog()  # Create dialog object
        import_product.exec_()  # Execute the dialog - show it

    def get_product_finished(self):
        """Slot for getProducts finished signal"""
        self.Product.load_()  # load_ products

    def master_data_action(self):
        """Slot for masterData triggered signal"""
        self.customerInfoStack.setCurrentIndex(0)

    def order_data_action(self):
        """Slot for orderData triggered signal"""
        self.customerInfoStack.setCurrentIndex(3)

    def populate_customer_list(self):
        """Populate customer tree"""
        self.customerList.clear()  # shake the tree for leaves
        self.customerList.setColumnCount(2)  # set columns
        self.customerList.setColumnWidth(0, 230)  # set width of name col
        self.customerList.setHeaderLabels(["Firma", "Konto"])
        self.customerList.setSortingEnabled(True)  # enable sorting
        items = []  # temporary list
        for c in self.Customer.customer_list:
            # create_ Widget
            item = QTreeWidgetItem([c["company"], c["account"]])
            items.append(item)
        # assign Widgets to Tree
        self.customerList.addTopLevelItems(items)

    def resizeEvent(self, event):
        """Slot for the resize event signal
        intended use is resize content to window
        """
        pass

    def settings_dialog_action(self):
        """Slot for settingsDialog triggered signal"""
        settings_dialog = SettingsDialog(self.Settings.current_settings)
        if settings_dialog.exec_():
            # do check if password has been changed
            # and hash it if necessary
            check = settings_dialog.app_settings
            if len(check["userpass"]) < 97:
                check["userpass"] = util.passwdfn.hash_password(check["userpass"])
            if len(check["mailpass"]) < 97:
                check["mailpass"] = util.passwdfn.hash_password(check["mailpass"])
            # assign new settings
            self.Settings.current_settings = check
            # save to database
            self.Settings.update_()
        else:
            pass

    def update_customer_action(self):
        """Slot for updateCustomer triggered signal"""
        if not self.currentCustomer:
            # msgbox triggered if no customer is selected
            msgbox = QMessageBox()
            msgbox.information(self,
                               "Eordre NG",
                               "Hvad vil du opdatere?",
                               QMessageBox.Ok)
            return False
        # assign input field values to customer object
        self.currentCustomer["company"] = self.txtCompany.text()
        self.currentCustomer["address1"] = self.txtAddress1.text()
        self.currentCustomer["address2"] = self.txtAddress2.text()
        self.currentCustomer["zipcode"] = self.txtZipCode.text()
        self.currentCustomer["city"] = self.txtCityName.text()
        self.currentCustomer["phone1"] = self.txtPhone1.text()
        self.currentCustomer["phone2"] = self.txtPhone2.text()
        self.currentCustomer["email"] = self.txtEmail.text()
        self.currentCustomer["factor"] = self.txtFactor.text()
        self.currentCustomer["infotext"] = self.txtInfoText.toPlainText()
        self.currentCustomer["modified"] = 1
        self.Customer.update_(list(self.currentCustomer.values()))

    def visit_data_action(self):
        """Slot for visitData triggered signal"""
        self.customerInfoStack.setCurrentIndex(2)

    def zero_database_action(self):
        """Slot for zeroDatabase triggered signal"""
        for tbl in config.CSVDATA:
            dbfn.recreate_table(tbl[1])
        self.customerList.clear()
        self.Product.load_()
        self.Customer.load_()
        msgbox = QMessageBox()
        msgbox.information(self,
                           "Eordre NG",
                           "Databasen er nulstillet!",
                           QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAutoSipEnabled(True)
    app.setDesktopSettingsAware(True)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    pixmap = QPixmap(":/graphics/splash/splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()

    app.processEvents()

    window = MainWindow()
    window.show()

    # QTimer.singleShot(1, window.app_run())
    QTimer.singleShot(1, window.app_run)
    splash.finish(window)

    sys.exit(app.exec_())
