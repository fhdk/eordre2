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

from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSplashScreen, QTreeWidgetItem

import resources.splash_rc

from configuration import config, configfn
from dialogs.csv_file_import_dialog import CsvFileImportDialog
from dialogs.get_customers_http_dialog import GetCustomersHttpDialog
from dialogs.get_products_http_dialog import GetProductsHttpDialog
from dialogs.report_dialog_create import ReportDialogCreate
from dialogs.settings_dialog import SettingsDialog
from dialogs.visit_dialog import VisitDialog
from models.contact import Contact
from models.customer import Customer
from models.detail import Detail
from models.employee import Employee
from models.product import Product
from models.report import Report
from models.settings import Settings
from models.visit import Visit
from resources.main_window_rc import Ui_mainWindow
from util import utils
from util.rules import check_settings

__appname__ = "Eordre NG"
__module__ = "main"

BC = "\033[1;36m"
EC = "\033[0;1m"
DBG = True


def printit(string):
    """
    Print variable string when debugging
    Args:
        string: the string to be printed
    """
    print("{}\n{}{}{}".format(__module__, BC, string, EC))


class MainWindow(QMainWindow, Ui_mainWindow):
    """
    Main Application Window
    """

    def __init__(self, parent=None):
        """
        Initialize MainWindow class
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        QThread.currentThread().setObjectName("main")
        configfn.check_config_folder()  # Check app folder in users home

        self.txtWorkdate.setText(datetime.date.today().isoformat())  # initialize workdate to current date
        self.contacts = Contact()  # Initialize Contact object
        self.customers = Customer()  # Initialize Customer object
        self.details = Detail()  # Initialize Detail object
        self.employees = Employee()  # Initialize Employee object
        self.products = Product()  # Initialize Product object
        self.reports = Report()  # Initialize Report object
        self.visits = Visit()  # Initialize Visit object
        self.settings = Settings()  # Initialize Settings object

        # connect menu trigger signals
        self.actionAboutQt.triggered.connect(self.show_about_qt)
        self.actionAboutSoftware.triggered.connect(self.show_about_software)
        self.actionArchiveChanges.triggered.connect(self.archive_customer)
        self.actionContactsInfo.triggered.connect(self.show_contact_data_page)
        self.actionCreateCustomer.triggered.connect(self.create_customer)
        self.actionCreateVisit.triggered.connect(self.show_visit_dialog)
        self.actionImportCsvFiles.triggered.connect(self.show_csv_file_import_dialog)
        self.actionExit.triggered.connect(self.app_exit)
        self.actionGetCatalogHttp.triggered.connect(self.show_get_products_http_dialog)
        self.actionGetCustomersHttp.triggered.connect(self.show_get_customers_http_dialog)
        self.actionMasterInfo.triggered.connect(self.show_master_data_page)
        self.actionReport.triggered.connect(self.show_create_report_dialog)
        self.actionReportList.triggered.connect(self.show_reports_dialog)
        self.actionSettings.triggered.connect(self.show_settings_dialog)
        self.actionVisitsInfo.triggered.connect(self.show_visit_data_page)
        self.actionZeroDatabase.triggered.connect(self.zero_database)
        # buttons on top
        self.btnAddCustomer.clicked.connect(self.create_customer)
        self.btnCreateReportDialog.clicked.connect(self.show_create_report_dialog)
        # buttons for paging data
        self.btnShowContacts.clicked.connect(self.show_contact_data_page)
        self.btnShowMasterdata.clicked.connect(self.show_master_data_page)
        self.btnShowVisits.clicked.connect(self.show_visit_data_page)
        # button on master data page
        self.btnArchiveMasterdata.clicked.connect(self.archive_customer)
        # buttons on contacts data page
        self.btnArchiveContacts.clicked.connect(self.archive_contacts)
        self.btnAddContact.clicked.connect(self.add_contact)
        # button visit data page
        self.btnVisitDialog.clicked.connect(self.show_visit_dialog)
        # connect list changes
        self.widgetCustomerList.currentItemChanged.connect(self.on_customer_changed)
        self.widgetVisitList.currentItemChanged.connect(self.on_visit_changed)

    def closeEvent(self, event):
        """
        Slot for close event signal
        Args:
            event:

        intended use is warning about unsaved data
        """
        pass

    @pyqtSlot()
    def app_exit(self):
        """
        Slot for exit triggered signal
        """
        app.quit()

    def display_sync_status(self):
        """
        Update status fields
        """
        self.txtCustLocal.setText(self.settings.active["lsc"])
        self.txtCustServer.setText(self.settings.active["sac"])
        self.txtProdLocal.setText(self.settings.active["lsp"])
        self.txtProdServer.setText(self.settings.active["sap"])

    def populate_contact_list(self):
        """
        Populate the contactlist based on currently selected customer
        """
        # load contacts
        self.widgetContactList.clear()
        items = []
        try:
            self.contacts.contact_list = self.customers.active["customer_id"]
            for c in self.contacts.contact_list:
                item = QTreeWidgetItem([c["name"], c["department"], c["phone"], c["email"]])
                items.append(item)
        except IndexError as i:
            if DBG:
                printit(" ->populate_contact_list\n ->IndexError: {}".format(i))
        except KeyError as k:
            if DBG:
                printit(" ->populate_contact_list\n ->KeyError: {}".format(k))

        self.widgetContactList.addTopLevelItems(items)

    def populate_customer_list(self):
        """
        Populate customer list
        """
        self.widgetCustomerList.clear()  # shake the tree for leaves
        self.widgetCustomerList.setColumnCount(2)  # set columns
        self.widgetCustomerList.setHeaderLabels(["Telefon", "Firma"])
        items = []  # temporary list
        try:
            for c in self.customers.customer_list:
                item = QTreeWidgetItem([c["phone1"], c["company"]])
                items.append(item)
        except (IndexError, KeyError):
            pass
        # assign Widgets to Tree
        self.widgetCustomerList.addTopLevelItems(items)
        self.widgetCustomerList.setSortingEnabled(True)  # enable sorting

    def populate_visit_details_list(self):
        """
        Populate the details list based on the active visit
        """
        self.widgetVisitDetails.clear()
        self.txtPoNumber.setText("")
        self.txtSas.setText("")
        self.txtSale.setText("")
        self.txtTotal.setText("")
        self.lblApproved.setText("")
        self.lblSent.setText("")
        self.txtVisitInfoText.setText("")

        items = []
        try:
            self.details.details_list = self.visits.active["visit_id"]

            self.txtPoNumber.setText(self.visits.active["po_number"])
            self.txtSas.setText(str(self.visits.active["po_sas"]))
            self.txtSale.setText(str(self.visits.active["po_sale"]))
            self.txtTotal.setText(str(self.visits.active["po_total"]))
            self.lblSent.setText(utils.bool2dk(utils.int2bool(self.visits.active["po_sent"])))
            self.lblApproved.setText(utils.bool2dk(utils.int2bool(self.visits.active["po_approved"])))
            self.txtVisitInfoText.setText(self.visits.active["info_text"])

            for detail in self.details.details_list:
                item = QTreeWidgetItem([detail["linetype"], str(detail["pcs"]), detail["sku"], detail["text"],
                                        str(detail["price"]), str(detail["discount"]), detail["extra"]])
                items.append(item)
        except KeyError as k:
            if DBG:
                printit(" ->populate_details_list\n  ->KeyError: {}".format(k))
        except IndexError as i:
            if DBG:
                printit(" ->populate_details_list\n  ->IndexError: {}".format(i))
        self.widgetVisitDetails.addTopLevelItems(items)

    def populate_visit_list(self):
        """
        Populate the visitlist based on the active customer
        """
        # populate visit list table
        self.widgetVisitList.clear()
        # self.widgetVisitList.setColumnCount(5)
        self.widgetVisitList.setHeaderLabels(["Id", "Dato", "Navn", "Demo", "Salg"])
        self.widgetVisitList.setColumnWidth(0, 0)
        items = []
        try:
            self.visits.visit_list_customer = self.customers.active["customer_id"]
            for visit in self.visits.visit_list_customer:
                item = QTreeWidgetItem([str(visit["visit_id"]), visit["visit_date"], visit["po_buyer"],
                                        visit["prod_demo"], visit["prod_sale"]])
                items.append(item)
        except IndexError as i:
            if DBG:
                printit(" ->populate_visit_list\n ->IndexError: {}".format(i))
        except KeyError as k:
            if DBG:
                printit(" ->populate_visit_list\n ->KeyError: {}".format(k))
        self.widgetVisitList.addTopLevelItems(items)

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
        is_set = check_settings(self.settings.active)
        if is_set:
            try:
                _ = self.employees.active["fullname"]

            except KeyError:
                msgbox = QMessageBox()
                msgbox.about(self.mainGrid, __appname__, "Check din netværksforbindelse! Tak")
        else:
            msgbox = QMessageBox()
            msgbox.about(self.mainGrid, __appname__,
                         "Der er mangler i dine indstillinger.\n\nDisse skal tilpasses. Tak")
            self.settings_dialog()
        # load report for workdate if exist
        self.reports.load_report(self.txtWorkdate.text())
        # all customerlist
        self.populate_customer_list()
        if utils.int2bool(self.settings.active["sc"]):
            # check server data
            status = utils.refresh_sync_status(self.settings)
            self.settings.active["sac"] = status[0][1].split()[0]
            self.settings.active["sap"] = status[1][1].split()[0]
            self.settings.update()
        # update display
        self.display_sync_status()
        # Hide the id column
        self.widgetVisitList.setColumnHidden(0, True)

        self.widgetVisitDetails.setColumnWidth(0, 30)
        self.widgetVisitDetails.setColumnWidth(1, 30)
        self.widgetVisitDetails.setColumnWidth(2, 100)
        self.widgetVisitDetails.setColumnWidth(3, 150)
        self.widgetVisitDetails.setColumnWidth(4, 60)
        self.widgetVisitDetails.setColumnWidth(5, 40)

    @pyqtSlot()
    def add_contact(self):
        """
        Save changes made to contacts
        """
        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "# TODO add new contact", QMessageBox.Ok)

    @pyqtSlot()
    def archive_contacts(self):
        """
        Save changes made to contacts
        """
        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "# TODO save changes made to contacts", QMessageBox.Ok)

    @pyqtSlot()
    def archive_customer(self):
        """
        Slot for updateCustomer triggered signal
        """
        if not self.customers.active:
            # msgbox triggered if no current is selected
            msgbox = QMessageBox()
            msgbox.information(self,
                               __appname__,
                               "Det kan jeg ikke på nuværende tidspunkt!",
                               QMessageBox.Ok)
            return False
        # assign input field values to current object
        self.customers.active["company"] = self.txtCompany.text()
        self.customers.active["address1"] = self.txtAddress1.text()
        self.customers.active["address2"] = self.txtAddress2.text()
        self.customers.active["zipcode"] = self.txtZipCode.text()
        self.customers.active["city"] = self.txtCityName.text()
        self.customers.active["phone1"] = self.txtPhone1.text()
        self.customers.active["phone2"] = self.txtPhone2.text()
        self.customers.active["email"] = self.txtEmail.text()
        self.customers.active["factor"] = self.txtFactor.text()
        self.customers.active["infotext"] = self.txtCustomerInfoText.toPlainText()
        self.customers.active["modified"] = 1
        self.customers.update()

    @pyqtSlot()
    def create_customer(self):
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

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def on_customer_changed(self, current, previous):
        """
        Slot for treewidget current item changed signal
        Used to respond to changes in the currently selected current
        and update the related current info pages

        Args:
            current: currently selected item
            previous: previous selected item
        """
        try:
            phone = current.text(0)
            company = current.text(1)
            # move current customer
            # load customer
            self.customers.lookup(phone, company)
            # fields to lineedits
            self.txtAccount.setText(self.customers.active["account"])
            self.txtCompany.setText(self.customers.active["company"])
            self.txtAddress1.setText(self.customers.active["address1"])
            self.txtAddress2.setText(self.customers.active["address2"])
            self.txtZipCode.setText(self.customers.active["zipcode"])
            self.txtCityName.setText(self.customers.active["city"])
            self.txtPhone1.setText(self.customers.active["phone1"])
            self.txtPhone2.setText(self.customers.active["phone2"])
            self.txtEmail.setText(self.customers.active["email"])
            self.txtFactor.setText(str(self.customers.active["factor"]))
            self.txtCustomerInfoText.setText(self.customers.active["infotext"])
        except AttributeError as a:
            if DBG:
                printit(" ->current_customer_changed\n "
                        "  ->exception handled\n"
                        "  ->AttributeError: {}".format(a))
        except KeyError as k:
            if DBG:
                printit(" ->current_customer_changed\n"
                        "  ->exception handled\n"
                        "  ->KeyError: {}".format(k))
        # load customer infos
        self.populate_contact_list()
        self.populate_visit_list()
        self.populate_visit_details_list()

    @pyqtSlot()
    def on_csv_import_done(self):
        """
        Slog for csv import done signal
        """
        self.populate_customer_list()

    @pyqtSlot()
    def on_customers_done(self):
        """
        Slot for getCustomers finished signal
        """
        if DBG:
            printit(" ->signal recieved\n  ->on_customers_done")
        self.populate_customer_list()
        lsc = datetime.date.today().isoformat()
        self.txtCustLocal.setText(lsc)
        self.settings.active["lsc"] = lsc
        self.settings.update()

    @pyqtSlot()
    def on_products_done(self):
        """
        Slot for getProducts finished signal
        """
        if DBG:
            printit(" ->signal recieved\n  ->on_products_done")
        self.products.all()
        lsp = datetime.date.today().isoformat()
        self.txtProdLocal.setText(lsp)
        self.settings.active["lsp"] = lsp
        self.settings.update()

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def on_visit_changed(self, current, previous):
        """
        Response to current visit changed
        Args:
            current:
            previous:
        """
        try:
            if DBG:
                printit("  ->active_visit_changed\n"
                        "  ->visit_id: {}".format(current.text(0)))
            self.visits.active = current.text(0)
        except AttributeError as a:
            if DBG:
                printit("  ->active_visit_changed\n"
                        "   ->exception handled\n"  
                        "   ->AttributeError: {}".format(a))
        except KeyError as k:
            if DBG:
                printit("  ->active_visit_changed\n"
                        "   ->exception handled\n"
                        "   ->KeyError: {}".format(k))
        self.populate_visit_details_list()

    @pyqtSlot()
    def data_export(self):
        """
        Slot for dataExport triggered signal
        """
        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "TODO: Opret CSV data backup", QMessageBox.Ok)

    @pyqtSlot()
    def show_about_qt(self):
        """
        Slot for aboutQt triggered signal
        """
        msgbox = QMessageBox()
        msgbox.aboutQt(self, __appname__)

    @pyqtSlot()
    def show_about_software(self):
        """
        Slot for aboutSoftware triggered signal
        """
        msgbox = QMessageBox()
        msgbox.about(self, __appname__,
                     "Bygget med Python 3.6 og Qt5<br/><br/>Frede Hundewadt (c) 2017<br/><br/>"
                     "<a href='https://www.gnu.org/licenses/agpl.html'>https://www.gnu.org/licenses/agpl.html</a>")

    @pyqtSlot()
    def show_contact_data_page(self):
        """
        Slot for contactData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(1)

    @pyqtSlot()
    def show_create_report_dialog(self):
        """
        Slot for Report triggered signal
        """
        try:
            # check the report date
            # no report triggers KeyError which in turn launches the CreateReportDialog
            repdate = self.reports.active["repdate"]
            if not repdate == self.txtWorkdate.text():
                # if active report is not the same replace it with workdate
                self.reports.load_report(self.txtWorkdate.text())
                # trigger a KeyError if no report is current which launches the CreateReportDialog
                repdate = self.reports.active["repdate"]
                # check if the report is sent
                if self.reports.active["sent"] == 1:
                    # we do not allow visits to be created on a report which is closed
                    self.buttonCreateVisit.setEnabled(False)
                else:
                    self.buttonCreateVisit.setEnabled(True)
            infotext = "Rapport aktiv for: {}".format(repdate)
            msgbox = QMessageBox()
            msgbox.information(self, __appname__, infotext, QMessageBox.Ok)
            return True

        except KeyError:
            # Show report dialog
            create_report_dialog = ReportDialogCreate(self.txtWorkdate.text())
            if create_report_dialog.exec_():
                # user chosed to create a report
                self.txtWorkdate.setText(create_report_dialog.workdate)
                # try load a report for that date
                self.reports.load_report(self.txtWorkdate.text())
                try:
                    # did the user choose an existing report
                    _ = self.reports.active["repdate"]
                    infotext = "Eksisterende rapport hentet: {}".format(self.txtWorkdate.text())
                except KeyError:
                    # create the report
                    self.reports.create(self.employees.active, self.txtWorkdate.text())
                    infotext = "Rapport oprettet for: {}".format(self.txtWorkdate.text())
                msgbox = QMessageBox()
                msgbox.information(self, __appname__, infotext, QMessageBox.Ok)
                return True
            else:
                msgbox = QMessageBox()
                msgbox.information(self,
                                   __appname__,
                                   "Den aktive rapport er <strong>IKKE</strong> ændret!",
                                   QMessageBox.Ok)
                return False

    @pyqtSlot()
    def show_csv_file_import_dialog(self):
        """
        Slot for fileImport triggered signal
        """
        if self.customers.customer_list:
            msgbox = QMessageBox()
            msgbox.warning(self,
                           __appname__,
                           "<strong>Ved import slettes alle eksisterende data</strong>!<br/><br/>"
                           "Det er alt eller intet af hensyn til datas sammenhæng.<br/>"
                           "Du <strong>SKAL</strong> importere <strong>ALLE<strong> tabeller fra listen!<br/><br/>"
                           "<strong>Gør du ikke det giver det uløselige problemer</strong>!",
                           QMessageBox.Ok)
        # app, contact, customer, detail, employee, report, visit, tables
        import_dialog = CsvFileImportDialog(app, self.contacts, self.customers, self.details,
                                            self.employees, self.reports, self.visits,
                                            config.CSV_TABLES)
        import_dialog.sig_done.connect(self.on_csv_import_done)
        import_dialog.exec_()

    @pyqtSlot()
    def show_get_customers_http_dialog(self):
        """
        Slot for getCustomers triggered signal
        """
        import_customers = GetCustomersHttpDialog(app,
                                                  customers=self.customers,
                                                  employees=self.employees,
                                                  settings=self.settings)
        import_customers.sig_done.connect(self.on_customers_done)
        import_customers.exec_()

    @pyqtSlot()
    def show_get_products_http_dialog(self):
        """
        Slot for getProducts triggered signal
        """
        import_product = GetProductsHttpDialog(app,
                                               products=self.products,
                                               settings=self.settings)
        import_product.sig_done.connect(self.on_products_done)
        import_product.exec_()

    @pyqtSlot()
    def show_visit_data_page(self):
        """
        Slot for visitData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(2)

    @pyqtSlot()
    def show_master_data_page(self):
        """
        Slot for masterData triggered signal
        """
        self.widgetCustomerInfo.setCurrentIndex(0)

    @pyqtSlot()
    def show_reports_dialog(self):
        """
        Slot for Report List triggered signal
        """
        pass

    @pyqtSlot()
    def show_settings_dialog(self):
        """
        Slot for settingsDialog triggered signal
        """
        settings_dialog = SettingsDialog(self.settings)
        settings_dialog.exec_()

    @pyqtSlot()
    def show_visit_dialog(self):
        """
        Slot for launching the visit dialog
        """
        try:
            # do we have a report
            _ = self.reports.active["repdate"]
            active_report = True
        except KeyError:
            active_report = self.create_report_dialog()
        if active_report:
            try:
                # do we have a customer
                _ = self.customers.active["company"]
            except KeyError:
                msgbox = QMessageBox()
                msgbox.information(self, __appname__, "Ingen valgt kunde! Besøg kan ikke oprettes.", QMessageBox.Ok)
                return
            # Launch the visit dialog
            visit_dialog = VisitDialog(self.customers, self.employees, self.products,
                                       self.reports, self.visits)
            if visit_dialog.exec_():
                pass

    @pyqtSlot()
    def zero_database(self):
        """
        Slot for zeroDatabase triggered signal
        """
        self.contacts.recreate_table()
        self.customers.recreate_table()
        self.details.recreate_table()
        self.visits.recreate_table()
        self.reports.recreate_table()

        self.populate_contact_list()
        self.populate_visit_details_list()
        self.populate_visit_list()
        self.populate_customer_list()

        self.settings.active["lsc"] = ""
        self.settings.active["sac"] = ""
        self.settings.active["lsp"] = ""
        self.settings.active["sap"] = ""
        self.settings.update()
        self.display_sync_status()

        msgbox = QMessageBox()
        msgbox.information(self, __appname__, "Salgsdata er nulstillet!", QMessageBox.Ok)


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
