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
from models.contact import Contact
from models.customer  import Customer
from models.employee import Employee
from models.visit import Visit
from models.detail import Detail
from models.product import Product
from models.report import Report
from models.settings import Settings
from resources.main_window_rc import Ui_MainWindow
from util import httpfn, passwdfn, utils
from util.rules import check_settings

__appname__ = "Eordre NG"
__module__ = "main"


B_COLOR = "\033[0;34m"
E_COLOR = "\033[0;1m"


def printit(string):
    print("{}{}{}".format(B_COLOR, string, E_COLOR))


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
        self.contacts = Contact()  # Initialize contact object
        self.customers = Customer()  # Initialize Customer object
        self.employees = Employee()  # Initialize current object
        self.products = Product()  # Initialize Product object
        self.reports = Report()  # Initialize Report object
        self.visits = Visit()  # Initialize Visit object
        self.details = Detail()  # Initialize Visit details object
        self.settings = Settings()  # Initialize current object

        # connect menu trigger signals
        self.actionAboutQt.triggered.connect(self.about_qt_action)
        self.actionAboutSoftware.triggered.connect(self.about_software_action)
        self.actionArchiveChanges.triggered.connect(self.archive_customer_action)
        self.actionContactsInfo.triggered.connect(self.contact_data_action)
        self.actionCreateCustomer.triggered.connect(self.create_customer_action)
        self.actionCreateVisit.triggered.connect(self.create_visit_action)
        self.actionImportCsvFiles.triggered.connect(self.get_data_csv)
        self.actionExit.triggered.connect(self.exit)
        self.actionGetCatalogHttp.triggered.connect(self.get_product_http)
        self.actionGetCustomersHttp.triggered.connect(self.get_customers_http)
        self.actionMasterInfo.triggered.connect(self.master_data_action)
        self.actionReport.triggered.connect(self.report_action)
        self.actionReportList.triggered.connect(self.report_list_action)
        self.actionSettings.triggered.connect(self.settings_dialog_action)
        self.actionVisitsList.triggered.connect(self.visits_list_action)
        self.actionZeroDatabase.triggered.connect(self.zero_database_action)
        # connect list change
        self.widgetCustomers.currentItemChanged.connect(self.customer_changed)
        # connect buttons
        self.buttonArchiveChanges.clicked.connect(self.archive_customer_action)
        self.buttonContactData.clicked.connect(self.contact_data_action)
        self.buttonCreateCustomer.clicked.connect(self.create_customer_action)
        self.buttonCreateVisit.clicked.connect(self.create_visit_action)
        self.buttonMasterData.clicked.connect(self.master_data_action)
        self.buttonHistoryData.clicked.connect(self.visit_details_action)
        self.buttonReport.clicked.connect(self.report_action)

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
        if not self.customers.current:
            # msgbox triggered if no current is selected
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Det kan jeg ikke på nuværende tidspunkt!",
                               QMessageBox.Ok)
            return False
        # assign input field values to current object
        self.customers.current["company"] = self.txtCompany.text()
        self.customers.current["address1"] = self.txtAddress1.text()
        self.customers.current["address2"] = self.txtAddress2.text()
        self.customers.current["zipcode"] = self.txtZipCode.text()
        self.customers.current["city"] = self.txtCityName.text()
        self.customers.current["phone1"] = self.txtPhone1.text()
        self.customers.current["phone2"] = self.txtPhone2.text()
        self.customers.current["email"] = self.txtEmail.text()
        self.customers.current["factor"] = self.txtFactor.text()
        self.customers.current["infotext"] = self.txtInfoText.toPlainText()
        self.customers.current["modified"] = 1
        self.customers.update()

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
        self.widgetCustomerInfo.setCurrentIndex(1)

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
        if not self.reports.load_report(self.txtWorkdate.text()):
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Der er ingen dagsrapport for idag!",
                               QMessageBox.Ok)
            return False

        if self.customers.current:
            visit_dialog = VisitDialog(self.customers, self.employees, self.products,
                                       self.reports, self.visits, self.txtWorkdate.text())
            if visit_dialog.exec_():
                pass
        else:
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Ingen valgt kunde! Besøg kan ikke oprettes.",
                               QMessageBox.Ok)

    def customer_changed(self, current, previous):
        """
        Slot for treewidget current item changed signal
        Used to respond to changes in the currently selected current
        and update the related current info pages

        Args:
            current: currently selected item
            previous: previous selected item
        """
        self.customers.lookup_by_phone_company(current.text(0), current.text(1))
        try:
            self.txtAccount.setText(self.customers.current["account"])
            self.txtCompany.setText(self.customers.current["company"])
            self.txtAddress1.setText(self.customers.current["address1"])
            self.txtAddress2.setText(self.customers.current["address2"])
            self.txtZipCode.setText(self.customers.current["zipcode"])
            self.txtCityName.setText(self.customers.current["city"])
            self.txtPhone1.setText(self.customers.current["phone1"])
            self.txtPhone2.setText(self.customers.current["phone2"])
            self.txtEmail.setText(self.customers.current["email"])
            self.txtFactor.setText(str(self.customers.current["factor"]))
            self.txtInfoText.clear()
            self.txtInfoText.insertPlainText(self.customers.current["infotext"])
            self.contacts.load_for_customer(self.customers.current["customerid"])
            self.visits.load_by_customer(self.customers.current["customerid"])

        except (KeyError, AttributeError):
            # clear input lines
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
            # clear customer related internals
            self.visits.clear()
            self.details.clear()
            self.contacts.clear()

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
        self.txtCustLocal.setText(self.settings.current["lsc"])
        self.txtCustServer.setText(self.settings.current["sac"])
        self.txtProdLocal.setText(self.settings.current["lsp"])
        self.txtProdServer.setText(self.settings.current["sap"])

    def exit(self):
        """
        Slot for exit triggered signal
        """
        self.close_event(self)
        app.quit()

    def get_data_csv(self):
        """
        Slot for fileImport triggered signal
        """
        if self.customers.customers or self.reports.current:
            msgbox = QMessageBox()
            msgbox.warning(self,
                           __appname__,
                           "<strong>Ved import slettes alle eksisterende data</strong>!<br/><br/>"
                           "Det er alt eller intet. <br/>"
                           "Af hensyn til sammenkædning af data <strong>SKAL</strong>,<br/>"
                           "du importere <strong>ALLE<strong> tabeller der findes i listen!<br/><br/>"
                           "<strong>Importerer du ikke alle vil det give problemer</strong>!",
                           QMessageBox.Ok)
        import_dialog = FileImportDialog(self.contacts, self.customers, self.employees,
                                         self.reports, self.visits, self.details, config.CSVDATA)

        import_dialog.exec_()
        self.populate_customer_list()

    def file_import_customer_done(self):
        """
        Slot for current import done. Used to trigger populate_customer_list
        """
        self.populate_customer_list()

    def get_customers_http(self):
        """
        Slot for getCustomers triggered signal
        """
        import_customers = HttpCustImportDialog(customers=self.customers,
                                                employees=self.employees,
                                                settings=self.settings)
        import_customers.c.finished.connect(self.get_customers_finished)
        import_customers.exec_()

    def get_customers_finished(self):
        """
        Slot for getCustomers finished signal
        """
        self.populate_customer_list()
        lsc = datetime.date.today().isoformat()
        self.txtCustLocal.setText(lsc)
        self.settings.current["lsc"] = lsc
        self.settings.update()

    def get_product_http(self):
        """
        Slot for getProducts triggered signal
        """
        import_product = HttpProdImportDialog(products=self.products,
                                              settings=self.settings)
        import_product.c.finished.connect(self.get_product_finished)
        import_product.exec_()

    def get_product_finished(self):
        """
        Slot for getProducts finished signal
        """
        self.products.load()
        lsp = datetime.date.today().isoformat()
        self.txtProdLocal.setText(lsp)
        self.settings.current["lsp"] = lsp
        self.settings.update()

    def master_data_action(self):
        """
        Slot for masterData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(0)

    def visit_details_action(self):
        """
        Slot for orderData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(3)

    def populate_customer_list(self):
        """
        Populate current tree
        """

        self.widgetCustomers.clear()  # shake the tree for leaves
        self.widgetCustomers.setColumnCount(2)  # set columns
        # self.widgetCustomers.setColumnWidth(0, 230)  # set width of name col
        self.widgetCustomers.setHeaderLabels(["Telefon", "Firma"])
        self.widgetCustomers.setSortingEnabled(True)  # enable sorting
        items = []  # temporary list
        try:
            for c in self.customers.customers:
                # create Widget
                item = QTreeWidgetItem([c["phone1"], c["company"]])
                items.append(item)
        except IndexError:
            pass
        # assign Widgets to Tree
        self.widgetCustomers.addTopLevelItems(items)
        self.widgetCustomers.scrollToTop()

    def report_action(self):
        """
        Slot for Report triggered signal
        """
        try:
            repdate = self.reports.current["repdate"]
            print("main.py -> current -> repdate: " + repdate)
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
                self.reports.create(self.employee.current, self.txtWorkdate.text())

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
        settings_dialog = SettingsDialog(self.settings)
        settings_dialog.exec_()

    def visits_list_action(self):
        """
        Slot for visitData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(2)

    def zero_database_action(self):
        """
        Slot for zeroDatabase triggered signal
        """
        self.contacts.recreate_table()
        self.customers.recreate_table()
        self.details.recreate_table()
        self.visits.recreate_table()
        self.reports.recreate_table()

        self.widgetCustomers.clear()

        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "Salgsdata er nulstillet!", QMessageBox.Ok)

    def run(self):
        """
        Setup database and basic configuration
        """
        # current needs to be up for inet connection to work
        is_set = check_settings(self.settings.current)
        if is_set:
            try:
                _ = self.employees.current["fullname"]
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
        if utils.int2bool(self.settings.current["sc"]):
            self.statusbar.setToolTip("Checker server for opdateringer ...")
            status = utils.refresh_sync_status(self.settings)
            self.settings.current["sac"] = status[0][1].split()[0]
            self.settings.current["sap"] = status[1][1].split()[0]
            self.settings.update()
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
