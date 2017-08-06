#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Eordre application module
"""

import datetime
import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSplashScreen, QTreeWidgetItem

# import resources.splash_rc
from configuration import configfn, config
from dialogs.visit_dialog import VisitDialog
from dialogs.create_report_dialog import CreateReportDialog
from dialogs.file_import_dialog import FileImportDialog
from dialogs.http_cust_import_dialog import HttpCustImportDialog
from dialogs.http_prod_import_dialog import HttpProdImportDialog
from dialogs.settings_dialog import SettingsDialog
from models import contact, customer, employee, visit, saleline, product, report, settings
from resources.main_window_rc import Ui_MainWindow
from util import httpfn, passwdfn, utils
from util.rules import check_settings

__appname__ = "Eordre NG"
__module__ = "main"


# noinspection PyMethodMayBeStatic
class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Main Application Window
    """

    def __init__(self):
        """
        Initialize MainWindow class
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)

        configfn.check_config_folder()  # Check app folder in users home

        self.txtWorkdate.setText(datetime.date.today().isoformat())  # initialize workdate to current date
        self.Contacts = contact.Contact()  # Initialize Contact object
        self.Customers = customer.Customer()  # Initialize Customer object
        self.Employee = employee.Employee()  # Initialize Employee object
        self.Visits = visit.Visit()  # Initialize Visit object
        self.Salelines = saleline.Saleline()  # Initialize OrderLine object
        self.Products = product.Product()  # Initialize Product object
        self.Reports = report.Report()  # Initialize Report object
        self.Settings = settings.Settings()  # Initialize Settings object

        # connect menu trigger signals
        self.actionAboutQt.triggered.connect(self.about_qt_action)
        self.actionAboutSoftware.triggered.connect(self.about_software_action)
        self.actionArchiveChanges.triggered.connect(self.archive_customer_action)
        self.actionContactData.triggered.connect(self.contact_data_action)
        self.actionCreateCustomer.triggered.connect(self.create_customer_action)
        self.actionCreateVisit.triggered.connect(self.create_visit_action)
        self.actionCsvFileImport.triggered.connect(self.file_import_action)
        self.actionExit.triggered.connect(self.exit_action)
        self.actionHttpGetCatalog.triggered.connect(self.get_http_product_action)
        self.actionHttpGetCustomers.triggered.connect(self.get_http_customers_action)
        self.actionMasterData.triggered.connect(self.master_data_action)
        self.actionOrderData.triggered.connect(self.order_data_action)
        self.actionReport.triggered.connect(self.report_action)
        self.actionReportList.triggered.connect(self.report_list_action)
        self.actionSettings.triggered.connect(self.settings_dialog_action)
        self.actionVisitData.triggered.connect(self.visit_data_action)
        self.actionZeroDatabase.triggered.connect(self.zero_database_action)
        # connect list change
        self.customerList.currentItemChanged.connect(self.customer_changed_action)
        # connect buttons
        self.buttonArchiveChanges.clicked.connect(self.archive_customer_action)
        self.buttonContactData.clicked.connect(self.contact_data_action)
        self.buttonCreateCustomer.clicked.connect(self.create_customer_action)
        self.buttonCreateVisit.clicked.connect(self.create_visit_action)
        self.buttonMasterData.clicked.connect(self.master_data_action)
        self.buttonOrderData.clicked.connect(self.order_data_action)
        self.buttonReport.clicked.connect(self.report_action)
        self.buttonVisitData.clicked.connect(self.visit_data_action)

    def about_qt_action(self):
        """
        Slot for aboutQt triggered signal
        """
        msgbox = QMessageBox()
        msgbox.aboutQt(self, __appname__)

    def about_software_action(self):
        """
        Slot for aboutSoftware triggered signal
        """
        msgbox = QMessageBox()
        msgbox.about(self, __appname__,
                     "Bygget med Python 3.6 og Qt framework<br/><br/>Frede Hundewadt (c) 2017<br/><br/>"
                     "<a href='https://www.gnu.org/licenses/agpl.html'>https://www.gnu.org/licenses/agpl.html</a>")

    def archive_customer_action(self):
        """
        Slot for updateCustomer triggered signal
        """
        if not self.Customers.customer:
            # msgbox triggered if no customer is selected
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Det kan jeg ikke på nuværende tidspunkt!",
                               QMessageBox.Ok)
            return False
        # assign input field values to customer object
        self.Customers.customer["company"] = self.txtCompany.text()
        self.Customers.customer["address1"] = self.txtAddress1.text()
        self.Customers.customer["address2"] = self.txtAddress2.text()
        self.Customers.customer["zipcode"] = self.txtZipCode.text()
        self.Customers.customer["city"] = self.txtCityName.text()
        self.Customers.customer["phone1"] = self.txtPhone1.text()
        self.Customers.customer["phone2"] = self.txtPhone2.text()
        self.Customers.customer["email"] = self.txtEmail.text()
        self.Customers.customer["factor"] = self.txtFactor.text()
        self.Customers.customer["infotext"] = self.txtInfoText.toPlainText()
        self.Customers.customer["modified"] = 1
        self.Customers.update()

    def close_event(self, event):
        """
        Slot for close event signal
        Args:
            event:

        intended use is warning about unsaved data
        """
        pass

    def contact_data_action(self):
        """
        Slot for contactData triggered signal
        """
        self.customerInfoStack.setCurrentIndex(1)

    def create_customer_action(self):
        """
        Slot for createCustomer triggered signal
        """
        if not self.txtNewCompany.text() or not self.txtNewPhone1.text():
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Snap - Jeg mangler:\n Firma navn \n Telefon nummer",
                               QMessageBox.Ok)
        else:
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Gem kunde til database\n\n" +
                               self.txtNewCompany.text() + "\n" +
                               self.txtNewPhone1.text(),
                               QMessageBox.Ok)

    def create_visit_action(self):
        """
        Slot for createOrder triggered signal
        """
        if not self.Reports.load_report(self.txtWorkdate.text()):
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Der er ingen dagsrapport for idag!",
                               QMessageBox.Ok)
            return False

        if self.Customers.customer:
            visit_dialog = VisitDialog(self,
                                       self.Reports.report,
                                       self.Customers.customer,
                                       self.Employee.employee)
            if visit_dialog.exec_():
                pass
        else:
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Ingen kunder - ingen ordre!",
                               QMessageBox.Ok)

    def customer_changed_action(self, current, previous):
        """
        Slot for listbox current item changed signal
        Used to respond to changes in the currently selected customer
        and update the related customer info pages

        Args:
            current: currently selected item
            previous: previous selected item
        """
        print("customer_changed_action:\n    {}, {}".format(current.text(1), current.text(0)))
        self.Customers.lookup_by_phone_name(current.text(1), current.text(0))
        try:
            self.txtAccount.setText(self.Customers.customer["account"])
            self.txtCompany.setText(self.Customers.customer["company"])
            self.txtAddress1.setText(self.Customers.customer["address1"])
            self.txtAddress2.setText(self.Customers.customer["address2"])
            self.txtZipCode.setText(self.Customers.customer["zipcode"])
            self.txtCityName.setText(self.Customers.customer["city"])
            self.txtPhone1.setText(self.Customers.customer["phone1"])
            self.txtPhone2.setText(self.Customers.customer["phone2"])
            self.txtEmail.setText(self.Customers.customer["email"])
            self.txtFactor.setText(str(self.Customers.customer["factor"]))
            self.txtInfoText.clear()
            self.txtInfoText.insertPlainText(self.Customers.customer["infotext"])
            self.Contacts.load_for_customer(self.Customers.customer["customerid"])
            self.Visits.select_by_customer(self.Customers.customer["customerid"])

        except (KeyError, AttributeError):
            self.txtAccount.clear()
            self.txtCompany.clear()
            self.txtAddress1.clear()
            self.txtAddress2.clear()
            self.txtZipCode.clear()
            self.txtCityName.clear()
            self.txtPhone1.clear()
            self.txtPhone2.clear()
            self.txtEmail.clear()
            self.txtFactor.clear()
            self.txtInfoText.clear()
            self.Visits.clear()
            self.Salelines.clear()
            self.Contacts.clear()

    def data_export_action(self):
        """
        Slot for dataExport triggered signal
        """
        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "Opret CSV data backup", QMessageBox.Ok)

    def display_sync_status(self):
        """
        Update status fields
        """
        self.txtCustLocal.setText(self.Settings.settings["lsc"])
        self.txtCustServer.setText(self.Settings.settings["sac"])
        self.txtProdLocal.setText(self.Settings.settings["lsp"])
        self.txtProdServer.setText(self.Settings.settings["sap"])

    def exit_action(self):
        """
        Slot for exit triggered signal
        """
        self.close_event(self)
        app.quit()

    def file_import_action(self):
        """
        Slot for fileImport triggered signal
        """
        if self.Customers.customers or self.Reports.report:
            # Warn user that import deletes existing data
            msgbox = QMessageBox()
            msgbox.warning(self,
                           __appname__,
                           "<strong>Ved import slettes alle eksisterende data</strong>!<br/><br/>"
                           "Det er alt eller intet. <br/>"
                           "Af hensyn til sammenkædning af data <strong>SKAL</strong>,<br/>"
                           "du importere <strong>ALLE<strong> tabeller der findes i listen!<br/><br/>"
                           "<strong>Importerer du ikke alle vil det give problemer</strong>!",
                           QMessageBox.Ok)
        import_dialog = FileImportDialog(config.CSVDATA, self.Employee.employee)  # Create import dialog

        import_dialog.exec_()  # Execute the dialog - show it
        self.populate_customer_list()  # Reload the customer list

    def file_import_customer_done(self):
        """
        Slot for customer import done. Used to trigger populate_customer_list
        """
        self.populate_customer_list()

    def get_http_customers_action(self):
        """
        Slot for getCustomers triggered signal
        """
        import_customers = HttpCustImportDialog()  # Create dialog object
        import_customers.c.finished.connect(self.get_customers_finished)
        import_customers.exec_()  # Execute the dialog - show it

    def get_customers_finished(self):
        """
        Slot for getCustomers finished signal
        """
        self.populate_customer_list()  # select_by_customer customers
        lsc = datetime.date.today().isoformat()  # get sync date
        self.txtCustLocal.setText(lsc)  # get update display
        self.Settings.settings["lsc"] = lsc  # update settings
        print("{}".format(list(self.Settings.settings.values())))
        # self.Settings.update()  # save settings

    def get_http_product_action(self):
        """
        Slot for getProducts triggered signal
        """
        import_product = HttpProdImportDialog()  # Create dialog object
        import_product.c.finished.connect(self.get_product_finished)
        import_product.exec_()  # Execute the dialog - show it

    def get_product_finished(self):
        """
        Slot for getProducts finished signal
        """
        self.Products.load()  # select_by_customer products
        lsp = datetime.date.today().isoformat()  # get sync date
        self.txtProdLocal.setText(lsp)  # update display
        self.Settings.settings["lsp"] = lsp  # update settings
        self.Settings.update()  # save settings

    def master_data_action(self):
        """
        Slot for masterData triggered signal
        """
        self.customerInfoStack.setCurrentIndex(0)

    def order_data_action(self):
        """
        Slot for orderData triggered signal
        """
        self.customerInfoStack.setCurrentIndex(3)

    def populate_customer_list(self):
        """
        Populate customer tree
        """
        self.customerList.clear()  # shake the tree for leaves
        self.customerList.setColumnCount(2)  # set columns
        self.customerList.setColumnWidth(0, 230)  # set width of name col
        self.customerList.setHeaderLabels(["Firma", "Konto"])
        self.customerList.setSortingEnabled(True)  # enable sorting
        items = []  # temporary list
        for c in self.Customers.customers:
            # add Widget
            item = QTreeWidgetItem([c["company"], c["account"]])
            items.append(item)
        # assign Widgets to Tree
        self.customerList.addTopLevelItems(items)
        self.customerList.scrollToTop()

    def report_action(self):
        """
        Slot for Report triggered signal
        """
        try:
            repdate = self.Reports.report["repdate"]
            print("main.py -> report_action -> repdate: " + repdate)
            if not repdate == self.txtWorkdate.text():
                infotext = "Den aktive rapportdato er\ndato: {}\narbejdsdato: {}".format(
                    repdate, self.txtWorkdate.text())
                msgbox = QMessageBox()
                msgbox.information(self, __appname__, infotext, QMessageBox.Ok)

        except KeyError:
            create_report_dialog = CreateReportDialog(self.txtWorkdate.text())  # Create dialog
            if create_report_dialog.exec_():  # Execute dialog - show it
                self.txtWorkdate.setText(create_report_dialog.workdate)
                msgbox = QMessageBox()
                msgbox.information(self,
                                   __appname__,
                                   "Der er oprettet dagsrapport for <strong>{}</strong>!".format(
                                       self.txtWorkdate.text()),
                                   QMessageBox.Ok)
                self.Reports.create(self.Employee.employee, self.txtWorkdate.text())

            else:
                msgbox = QMessageBox()
                msgbox.information(self,
                                   __appname__,
                                   "Der er <strong>IKKE</strong> oprettet dagsrapport!",
                                   QMessageBox.Ok)

    def report_list_action(self):
        """
        Slot for Report List triggered signal
        """
        pass

    def resizeEvent(self, event):
        """
        Slot for the resize event signal
        Args:
            event:
        intended use is resize content to window
        """
        pass

    def settings_dialog_action(self):
        """
        Slot for settingsDialog triggered signal
        """
        settings_dialog = SettingsDialog(self.Settings.settings)
        if settings_dialog.exec_():
            # do check if password has been changed
            # and hash it if necessary
            check = settings_dialog.app_settings
            if len(check["userpass"]) < 97:
                check["userpass"] = passwdfn.hash_password(check["userpass"])
            if len(check["mailpass"]) < 97:
                check["mailpass"] = passwdfn.hash_password(check["mailpass"])
            # assign new settings
            self.Settings.settings = check
        else:
            pass

    def visit_data_action(self):
        """
        Slot for visitData triggered signal
        """
        self.customerInfoStack.setCurrentIndex(2)

    def zero_database_action(self):
        """
        Slot for zeroDatabase triggered signal
        """
        self.Contacts.recreate_table()
        self.Customers.recreate_table()
        self.Salelines.recreate_table()
        self.Visits.recreate_table()
        self.Reports.recreate_table()
        self.customerList.clear()
        self.Products.clear()
        self.Customers.clear()
        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "Salgsdata er nulstillet!", QMessageBox.Ok)

    def run(self):
        """
        Setup database and basic configuration
        """
        # Settings needs to be up for inet connection to work
        is_set = check_settings(self.Settings.settings)
        if is_set:
            try:
                _ = self.Employee.employee["fullname"]
            except KeyError:
                if httpfn.inet_conn_check():
                    pass
                else:
                    msgbox = QMessageBox()
                    msgbox.about(self,
                                 __appname__,
                                 "Check din netværksforbindelse! Tak")

        else:
            msgbox = QMessageBox()
            msgbox.about(self,
                         __appname__,
                         "Der er mangler i dine indstillinger.\n\nDisse skal tilpasses. Tak")
            self.settings_dialog_action()

        self.populate_customer_list()
        if utils.int2bool(self.Settings.settings["sc"]):
            self.statusbar.setToolTip("Checker server for opdateringer ...")
            status = utils.refresh_sync_status(self.Settings.settings)
            self.Settings.settings["sac"] = status[0][1].split()[0]
            self.Settings.settings["sap"] = status[1][1].split()[0]
            self.Settings.update()
        # update display
        self.display_sync_status()


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

    QTimer.singleShot(1, window.run)
    splash.finish(window)

    sys.exit(app.exec_())
