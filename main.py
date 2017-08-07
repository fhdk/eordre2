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
from dialogs.create_visit_dialog import CreateVisitDialog
from dialogs.create_report_dialog import CreateReportDialog
from dialogs.csv_file_import_dialog import CsvFileImportDialog
from dialogs.get_customers_http_dialog import GetCustomersHttpDialog
from dialogs.get_products_http_dialog import GetProductsHttpDialog
from dialogs.settings_dialog import SettingsDialog
from models.contact import Contact
from models.customer import Customer
from models.employee import Employee
from models.visit import Visit
from models.detail import Detail
from models.product import Product
from models.report import Report
from models.settings import Settings
from resources.main_window_rc import Ui_mainWindow
from util import httpfn, utils
from util.rules import check_settings

__appname__ = "Eordre NG"
__module__ = "main"

B_COLOR = "\033[0;34m"
E_COLOR = "\033[0;1m"


def printit(string):
    print("{}{}{}".format(B_COLOR, string, E_COLOR))


# noinspection PyMethodMayBeStatic
class MainWindow(QMainWindow, Ui_mainWindow):
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
        self.details = Detail()  # Initialize Visit details object
        self.employees = Employee()  # Initialize current object
        self.products = Product()  # Initialize Product object
        self.reports = Report()  # Initialize Report object
        self.visits = Visit()  # Initialize Visit object
        self.settings = Settings()  # Initialize current object

        # connect menu trigger signals
        self.actionAboutQt.triggered.connect(self.about_qt_action)
        self.actionAboutSoftware.triggered.connect(self.about_software_action)
        self.actionArchiveChanges.triggered.connect(self.action_archive_customer_changes)
        self.actionContactsInfo.triggered.connect(self.action_show_contact_data)
        self.actionCreateCustomer.triggered.connect(self.action_create_customer)
        self.actionCreateVisit.triggered.connect(self.action_visit_dialog_show)
        self.actionImportCsvFiles.triggered.connect(self.action_file_import_dialog_show)
        self.actionExit.triggered.connect(self.action_exit)
        self.actionGetCatalogHttp.triggered.connect(self.action_get_product_http_dialog_show)
        self.actionGetCustomersHttp.triggered.connect(self.action_get_customers_http_dialog_show)
        self.actionMasterInfo.triggered.connect(self.action_show_master_data)
        self.actionReport.triggered.connect(self.action_create_report_dialog_show)
        self.actionReportList.triggered.connect(self.action_show_reports)
        self.actionSettings.triggered.connect(self.action_settings_dialog_show)
        self.actionVisitsInfo.triggered.connect(self.action_show_history_data)
        self.actionZeroDatabase.triggered.connect(self.action_zero_database)
        # connect list change
        self.widgetCustomers.currentItemChanged.connect(self.action_customer_changed_signal)
        # connect buttons
        self.buttonArchiveChanges.clicked.connect(self.action_archive_customer_changes)
        self.buttonContactData.clicked.connect(self.action_show_contact_data)
        self.buttonCreateCustomer.clicked.connect(self.action_create_customer)
        self.buttonCreateVisit.clicked.connect(self.action_visit_dialog_show)
        self.buttonMasterData.clicked.connect(self.action_show_master_data)
        self.buttonHistoryData.clicked.connect(self.action_show_history_data)
        self.buttonReport.clicked.connect(self.action_create_report_dialog_show)

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

    def action_archive_customer_changes(self):
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

    def action_create_customer(self):
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

    def action_visit_dialog_show(self):
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
            visit_dialog = CreateVisitDialog(self.customers, self.employees, self.products,
                                             self.reports, self.visits, self.txtWorkdate.text())
            if visit_dialog.exec_():
                pass
        else:
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Ingen valgt kunde! Besøg kan ikke oprettes.",
                               QMessageBox.Ok)

    def action_customer_changed_signal(self, current, previous):
        """
        Slot for treewidget current item changed signal
        Used to respond to changes in the currently selected current
        and update the related current info pages

        Args:
            current: currently selected item
            previous: previous selected item
        """
        self.customers.current = current.text(0), current.text(1)
        print("{}".format(self.customers.current))
        # try:
        self.txtAccount.setText(str(self.customers.current["account"]))
        self.txtCompany.setText(self.customers.current["company"])
        self.txtAddress1.setText(self.customers.current["address1"])
        self.txtAddress2.setText(self.customers.current["address2"])
        self.txtZipCode.setText(str(self.customers.current["zipcode"]))
        self.txtCityName.setText(self.customers.current["city"])
        self.txtPhone1.setText(str(self.customers.current["phone1"]))
        self.txtPhone2.setText(str(self.customers.current["phone2"]))
        self.txtEmail.setText(self.customers.current["email"])
        self.txtFactor.setText(str(self.customers.current["factor"]))
        self.txtInfoText.setText(self.customers.current["infotext"])

        self.contacts.load_for_customer(self.customers.current["customer_id"])

        self.visits.load_by_customer(self.customers.current["customer_id"])

        # except (KeyError, AttributeError):
        #     # clear input lines
        #     self.txtAccount.clear()
        #     self.txtCompany.clear()
        #     self.txtAddress1.clear()
        #     self.txtAddress2.clear()
        #     self.txtZipCode.clear()
        #     self.txtCityName.clear()
        #     self.txtPhone1.clear()
        #     self.txtPhone2.clear()
        #     self.txtEmail.clear()
        #     self.txtFactor.clear()
        #     self.txtInfoText.clear()
        #     # clear customer related internals
        #     self.visits.clear()
        #     self.details.clear()
        #     self.contacts.clear()

    def action_data_export(self):
        """
        Slot for dataExport triggered signal
        """
        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "Opret CSV data backup", QMessageBox.Ok)

    def action_file_import_dialog_show(self):
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
        import_dialog = CsvFileImportDialog(self.contacts, self.customers, self.details,
                                            self.employees, self.reports, self.visits, config.CSV_TABLES)

        import_dialog.exec_()
        self.populate_customer_list()

    def action_get_csv_data_customer_done_signal(self):
        """
        Slot for current import done. Used to trigger populate_customer_list
        """
        self.populate_customer_list()

    def action_get_customers_http_dialog_show(self):
        """
        Slot for getCustomers triggered signal
        """
        import_customers = GetCustomersHttpDialog(customers=self.customers,
                                                  employees=self.employees,
                                                  settings=self.settings)
        import_customers.c.finished.connect(self.action_get_customers_http_done_signal)
        import_customers.exec_()

    def action_get_customers_http_done_signal(self):
        """
        Slot for getCustomers finished signal
        """
        self.populate_customer_list()
        lsc = datetime.date.today().isoformat()
        self.txtCustLocal.setText(lsc)
        self.settings.current["lsc"] = lsc
        self.settings.update()

    def action_get_product_http_dialog_show(self):
        """
        Slot for getProducts triggered signal
        """
        import_product = GetProductsHttpDialog(products=self.products,
                                               settings=self.settings)
        import_product.c.finished.connect(self.action_get_product_http_done_signal)
        import_product.exec_()

    def action_get_product_http_done_signal(self):
        """
        Slot for getProducts finished signal
        """
        self.products.load()
        lsp = datetime.date.today().isoformat()
        self.txtProdLocal.setText(lsp)
        self.settings.current["lsp"] = lsp
        self.settings.update()

    def action_create_report_dialog_show(self):
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

    def action_settings_dialog_show(self):
        """
        Slot for settingsDialog triggered signal
        """
        settings_dialog = SettingsDialog(self.settings)
        settings_dialog.exec_()

    def action_show_contact_data(self):
        """
        Slot for contactData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(1)

    def action_show_history_data(self):
        """
        Slot for visitData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(2)

    def action_show_master_data(self):
        """
        Slot for masterData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(0)

    def action_show_reports(self):
        """
        Slot for Report List triggered signal
        """
        pass

    def action_zero_database(self):
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

    def closeEvent(self, event):
        """
        Slot for close event signal
        Args:
            event:

        intended use is warning about unsaved data
        """
        pass

    def action_exit(self):
        """
        Slot for action_exit triggered signal
        """
        app.quit()

    def display_sync_status(self):
        """
        Update status fields
        """
        self.txtCustLocal.setText(self.settings.current["lsc"])
        self.txtCustServer.setText(self.settings.current["sac"])
        self.txtProdLocal.setText(self.settings.current["lsp"])
        self.txtProdServer.setText(self.settings.current["sap"])

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
                item = QTreeWidgetItem([c["phone1"], c["company"]])
                items.append(item)
        except IndexError:
            pass
        # assign Widgets to Tree
        self.widgetCustomers.addTopLevelItems(items)
        self.widgetCustomers.scrollToTop()

    def resizeEvent(self, event):
        """
        Slot for the resize event signal
        Args:
            event:
        intended use is resize content to window
        """
        pass

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
            self.action_settings_dialog_show()

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
