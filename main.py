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
from configuration import configfn, config
from dialogs.visit_dialog import CreateOrderDialog
from dialogs.create_report_dialog import CreateReportDialog
from dialogs.file_import_dialog import FileImportDialog
from dialogs.http_cust_import_dialog import HttpCustImportDialog
from dialogs.http_prod_import_dialog import HttpProdImportDialog
from dialogs.settings_dialog import SettingsDialog
from models import contact, customer, employee, visit, orderline, product, report, settings
from resources.main_window_rc import Ui_MainWindow
from util import httpfn, dbfn, passwdfn, utils
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

        self.txtWorkdate.setText(datetime.date.today().isoformat())  # initialize workdate to current date
        self.Contacts = contact.Contact()  # Initialize Contact object
        self.Customers = customer.Customer()  # Initialize Customer object
        self.Employee = employee.Employee()  # Initialize Employee object
        self.Visits = visit.Visit()  # Initialize OrderVisit object
        self.OrderLines = orderline.OrderLine()  # Initialize OrderLine object
        self.Products = product.Product()  # Initialize Product object
        self.Reports = report.Report()  # Initialize Report object
        self.Settings = settings.Setting()  # Initialize Settings object

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
        """Slot for aboutQt triggered signal"""
        msgbox = QMessageBox()
        msgbox.aboutQt(self, __appname__)

    def about_software_action(self):
        """Slot for aboutSoftware triggered signal"""
        msgbox = QMessageBox()
        msgbox.about(self, __appname__,
                     "Bygget med Python 3.6 og Qt framework<br/><br/>Frede Hundewadt (c) 2017<br/><br/>"
                     "<a href='https://www.gnu.org/licenses/agpl.html'>https://www.gnu.org/licenses/agpl.html</a>")

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
                         __appname__,
                         "Der er mangler i dine indstillinger.\n\nDisse skal tilpasses.")
            self.settings_dialog_action()

        self.populate_customer_list()
        if utils.int2bool(self.Settings.current_settings["sc"]):
            self.statusbar.setToolTip("Checker server for opdateringer ...")
            status = utils.refresh_sync_status(self.Settings.current_settings)
            self.Settings.current_settings["sac"] = status[0][1].split()[0]
            self.Settings.current_settings["sap"] = status[1][1].split()[0]
            self.Settings.update_()
        # update display
        self.display_sync_status()

    def archive_customer_action(self):
        """Slot for updateCustomer triggered signal"""
        if not self.Customers.current_customer:
            # msgbox triggered if no customer is selected
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Det kan jeg ikke på nuværende tidspunkt!",
                               QMessageBox.Ok)
            return False
        # assign input field values to customer object
        self.Customers.current_customer["company"] = self.txtCompany.text()
        self.Customers.current_customer["address1"] = self.txtAddress1.text()
        self.Customers.current_customer["address2"] = self.txtAddress2.text()
        self.Customers.current_customer["zipcode"] = self.txtZipCode.text()
        self.Customers.current_customer["city"] = self.txtCityName.text()
        self.Customers.current_customer["phone1"] = self.txtPhone1.text()
        self.Customers.current_customer["phone2"] = self.txtPhone2.text()
        self.Customers.current_customer["email"] = self.txtEmail.text()
        self.Customers.current_customer["factor"] = self.txtFactor.text()
        self.Customers.current_customer["infotext"] = self.txtInfoText.toPlainText()
        self.Customers.current_customer["modified"] = 1
        self.Customers.save_()

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
        """Slot for createOrder triggered signal"""
        if not self.Reports.load_report(self.txtWorkdate.text()):
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Der er ingen dagsrapport for idag!",
                               QMessageBox.Ok)
            return False

        if self.Customers.current_customer:
            order_dialog = CreateOrderDialog(self,
                                             self.Reports.current_report,
                                             self.Customers.current_customer,
                                             self.Employee.current_employee)
            if order_dialog.exec_():
                pass
        else:
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Ingen kunder - ingen ordre!",
                               QMessageBox.Ok)

    def customer_changed_action(self, current, previous):
        """Slot for listbox current item changed signal
        propagate changes to currently selected customer
        to related customer info pages
        :param current: currently selected item
        :param previous: previous selected item
        """
        self.Customers.find_name_account(current.text(0), current.text(1))
        try:
            self.txtAccount.setText(self.Customers.current_customer["account"])
            self.txtCompany.setText(self.Customers.current_customer["company"])
            self.txtAddress1.setText(self.Customers.current_customer["address1"])
            self.txtAddress2.setText(self.Customers.current_customer["address2"])
            self.txtZipCode.setText(self.Customers.current_customer["zipcode"])
            self.txtCityName.setText(self.Customers.current_customer["city"])
            self.txtPhone1.setText(self.Customers.current_customer["phone1"])
            self.txtPhone2.setText(self.Customers.current_customer["phone2"])
            self.txtEmail.setText(self.Customers.current_customer["email"])
            self.txtFactor.setText(str(self.Customers.current_customer["factor"]))
            self.txtInfoText.clear()
            self.txtInfoText.insertPlainText(self.Customers.current_customer["infotext"])
            self.Contacts.load_for_customer(self.Customers.current_customer["customerid"])
            self.Visits.load_for_customer(self.Customers.current_customer["customerid"])

        except KeyError:
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
            self.OrderLines.clear()
            self.Contacts.clear()

    def data_export_action(self):
        """Slot for dataExport triggered signal"""
        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "Opret CSV data backup", QMessageBox.Ok)

    def display_sync_status(self):
        self.txtCustLocal.setText(self.Settings.current_settings["lsc"])
        self.txtCustServer.setText(self.Settings.current_settings["sac"])
        self.txtProdLocal.setText(self.Settings.current_settings["lsp"])
        self.txtProdServer.setText(self.Settings.current_settings["sap"])

    def exit_action(self):
        """Slot for exit triggered signal"""
        self.close_event(self)
        app.quit()

    def file_import_action(self):
        """Slot for fileImport triggered signal"""
        if self.Customers.customer_list or self.Reports.current_report:
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
        import_dialog = FileImportDialog(config.CSVDATA, self.Employee.current_employee)  # Create import dialog

        if import_dialog.exec_():  # Execute the dialog - show it
            self.populate_customer_list()  # Reload the customer list
        else:
            pass

    def file_import_customer_done(self):
        """Slot for customer import done. Used to trigger populate_customer_list"""
        self.populate_customer_list()

    def get_http_customers_action(self):
        """Slot for getCustomers triggered signal"""
        import_customers = HttpCustImportDialog()  # Create dialog object
        import_customers.c.finished.connect(self.get_customers_finished)
        import_customers.exec_()  # Execute the dialog - show it

    def get_customers_finished(self):
        """Slot for getCustomers finished signal"""
        self.populate_customer_list()  # load_for_customer customers
        lsc = datetime.date.today().isoformat()  # get sync date
        self.txtCustLocal.setText(lsc)  # get update display
        self.Settings.current_settings["lsc"] = lsc  # update settings
        print("{}".format(list(self.Settings.current_settings.values())))
        # self.Settings.update_()  # save settings

    def get_http_product_action(self):
        """Slot for getProducts triggered signal"""
        import_product = HttpProdImportDialog()  # Create dialog object
        import_product.c.finished.connect(self.get_product_finished)
        import_product.exec_()  # Execute the dialog - show it

    def get_product_finished(self):
        """Slot for getProducts finished signal"""
        self.Products.load_()  # load_for_customer products
        lsp = datetime.date.today().isoformat()  # get sync date
        self.txtProdLocal.setText(lsp)  # update display
        self.Settings.current_settings["lsp"] = lsp  # update settings
        self.Settings.update_()  # save settings

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
        for c in self.Customers.customer_list:
            # create Widget
            item = QTreeWidgetItem([c["company"], c["account"]])
            items.append(item)
        # assign Widgets to Tree
        self.customerList.addTopLevelItems(items)
        self.customerList.scrollToTop()

    def report_action(self):
        """Slot for Report triggered signal"""
        try:
            repdate = self.Reports.current_report["repdate"]
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
                self.Reports.create_(self.Employee.current_employee, self.txtWorkdate.text())

            else:
                msgbox = QMessageBox()
                msgbox.information(self,
                                   __appname__,
                                   "Der er <strong>IKKE</strong> oprettet dagsrapport!",
                                   QMessageBox.Ok)

    def report_list_action(self):
        """Slot for Report List triggered signal"""
        pass

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
                check["userpass"] = passwdfn.hash_password(check["userpass"])
            if len(check["mailpass"]) < 97:
                check["mailpass"] = passwdfn.hash_password(check["mailpass"])
            # assign new settings
            self.Settings.current_settings = check
            # save to database
            self.Settings.update_()
            self.Employee.load_()
        else:
            pass

    def visit_data_action(self):
        """Slot for visitData triggered signal"""
        self.customerInfoStack.setCurrentIndex(2)

    def zero_database_action(self):
        """Slot for zeroDatabase triggered signal"""
        for tbl in config.CSVDATA:
            dbfn.recreate_table(tbl[1])
        self.customerList.clear()
        self.Products.clear()
        self.Customers.clear()
        msgbox = QMessageBox()
        msgbox.information(self,
                           __appname__,
                           "Kunder og prisliste er nu nulstillet!",
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
