#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# Copyright: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Visit Dialog Module
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QTableWidgetItem

from models.detail import Detail
from resources.visit_dialog_rc import Ui_visitDialog
from util import utils


class VisitDialog(QDialog, Ui_visitDialog):
    """
    Dialog for creating a new current
    """

    def __init__(self, customer, employee, product, report, visit, parent=None):
        """
        Initialize
        Args:
            customer:
            employee:
            product:
            report:
            visit:
            parent:
        """
        super(VisitDialog, self).__init__(parent)
        self.setupUi(self)
        self.customerid = customer.active["customer_id"]
        self.employeeid = employee.active["employee_id"]
        self.reportid = report.active["report_id"]
        self.workdate = report.active["rep_date"]
        self.products = product.product_list
        self.txtVisitDate.setText(self.workdate)

        self.visits = visit
        try:

            v = self.visits.find_by_date(self.workdate)
            v_id = v["visit_id"]

        except KeyError:
            self.visits.add(self.reportid, self.employeeid, self.customerid, self.workdate)
            if customer.active["account"] == "NY":
                self.visitType = "N"
            else:
                self.visitType = "R"
            self.visits.active["visit_type"] = self.visitType

        self.details = Detail()
        self.details.load(self.visits.active["visit_id"])
        for idx, detail in enumerate(self.details.details_list):
            # "pcs", "sku", "text", "price", "sas", "discount", "linetype", "extra"
            row_count = idx + 1
            self.widgetVisitDetails.setRowCount(row_count)
            self.widgetVisitDetails.setRowHeight(row_count, 20)
            w = QTableWidgetItem()
            w.setText(detail["linetype"])
            self.widgetVisitDetails.setItem(row_count, 0, w)
            w.setText(str(detail["pcs"]))
            self.widgetVisitDetails.setItem(row_count, 1, w)
            w.setText(detail["item"])
            self.widgetVisitDetails.setItem(row_count, 2, w)
            w.setText(detail["sku"])
            self.widgetVisitDetails.setItem(row_count, 3, w)
            w.setText(detail["text"])
            self.widgetVisitDetails.setItem(row_count, 4, w)
            w.setText(str(detail["price"]))
            self.widgetVisitDetails.setItem(row_count, 5, w)
            w.setText(str(detail["discount"]))
            self.widgetVisitDetails.setItem(row_count, 6, w)
            w.setText(str(detail["amount"]))
            self.widgetVisitDetails.setItem(row_count, 7, w)
            w.setText(utils.int2str_dk(detail["sas"]))
            self.widgetVisitDetails.setItem(row_count, 8, w)
            w.setText(detail["extra"])
            self.widgetVisitDetails.setItem(row_count, 9, w)

        # If customer needs special settings on prices
        factor = customer.active["factor"]
        if factor > 0.0:
            for item in self.products:
                item["price"] = item["price"] * factor
                if not item["d2"] == 0.0:
                    item["d2"] = item["d2"] * factor
                if not item["d3"] == 0.0:
                    item["d3"] = item["d3"] * factor
                if not item["d4"] == 0.0:
                    item["d4"] = item["d4"] * factor
                if not item["d6"] == 0.0:
                    item["d6"] = item["d6"] * factor
                if not item["d8"] == 0.0:
                    item["d8"] = item["d8"] * factor
                if not item["d12"] == 0.0:
                    item["d12"] = item["d12"] * factor
                if not item["d24"] == 0.0:
                    item["d24"] = item["d24"] * factor
                if not item["d2"] == 0.0:
                    item["d48"] = item["d48"] * factor
                if not item["d96"] == 0.0:
                    item["d96"] = item["d96"] * factor
                if not item["min"] == 0.0:
                    item["min"] = item["min"] * factor
                if not item["net"] == 0.0:
                    item["net"] = item["net"] * factor
        # Set info banner
        self.txtCompany.setText(customer.active["company"])
        # connect to signals
        self.btnAppend.clicked.connect(self.button_add_line_action)
        self.btnClear.clicked.connect(self.button_clear_line_action)
        self.btnArchiveVisit.clicked.connect(self.button_save_visit_action)
        self.cboDnst.currentIndexChanged.connect(self.dnst_changed_action)
        self.widgetVisitDetails.setColumnWidth(0, 43)   # line_type D/N/S
        self.widgetVisitDetails.setColumnWidth(1, 44)   # pcs
        self.widgetVisitDetails.setColumnWidth(2, 83)   # product
        self.widgetVisitDetails.setColumnWidth(3, 123)  # sku
        self.widgetVisitDetails.setColumnWidth(4, 153)  # text
        self.widgetVisitDetails.setColumnWidth(5, 60)   # price
        self.widgetVisitDetails.setColumnWidth(6, 50)   # discount
        self.widgetVisitDetails.setColumnWidth(7, 60)   # amount
        self.widgetVisitDetails.setColumnWidth(8, 30)   # SAS

    @pyqtSlot()
    def button_add_line_action(self):
        """
        Slot for Add Demo button clicked
        """
        new_row = self.widgetVisitDetails.rowCount() + 1
        self.widgetVisitDetails.setRowCount(new_row)
        self.widgetVisitDetails.setRowHeight(new_row, 20)

    @pyqtSlot()
    def button_clear_line_action(self):
        """
        Slot for Add Demo button clicked
        """

    @pyqtSlot()
    def button_save_visit_action(self):
        """
        Slot for saving the visit
        """
        # save visit head contents
        self.visits.active["po_buyer"] = self.txtPoBuyer.text()
        self.visits.active["po_number"] = self.txtPoNumber.text()
        self.visits.active["po_company"] = self.txtPoCompany.text()
        self.visits.active["po_address1"] = self.txtPoAddress1.text()
        self.visits.active["po_address2"] = self.txtPoAddress2.text()
        self.visits.active["po_postcode"] = self.txtPoPostcode.text()
        self.visits.active["po_postofffice"] = self.txtPoPostoffice.text()
        self.visits.active["po_country"] = self.txtPoCountry.text()
        self.visits.active["info_text"] = self.txtInfoText.toPlainText()
        self.visits.active["prod_demo"] = self.txtProductDemo.text()
        self.visits.active["prod_sale"] = self.txtProductSale.text()
        self.visits.active["sas"] = self.txtVisitSas.text()
        self.visits.active["sale"] = self.txtVisitSale.text()
        self.visits.active["total"] = self.txtVisitTotal.text()

        # TODO: save visitdetails

    @pyqtSlot()
    def dnst_changed_action(self):
        """
        Changed linetype
        :return: nothing
        """
        if self.cboDnst.currentText() == "T":
            self.set_input_enabled(False)
            return
        self.set_input(True)

    def set_input_enabled(self, arg: bool):
        """Enable inputs"""
        self.txtPcs.setEnabled(arg)
        self.cboProduct.setEnabled(arg)
        self.cboSku.setEnabled(arg)
        self.txtLinePrice.setEnabled(arg)
        self.txtLineDiscount.setEnabled(arg)
        self.chkSas.setEnabled(arg)

    def load_items(self):
        """Load ITEMS into product combo"""
        for item in self.products:
            self.cboProduct.addItem(item["item"], item["sku"])

    def load_sku(self):
        """Load SKU into sku combo"""
        for item in self.products:
            self.cboProduct.addItem(item["sku"], item["name1"])

    def item_changed_action(self):
        """Update SKU combo when item changes"""
        self.cboSku.setCurrentText(self.cboProduct.itemData(self.cboProduct.currentIndex()))

    def sku_changed_action(self):
        """Update ITEM combo when sku changes"""
        self.txtLineText.setText(self.cboSku.itemData(self.cboSku.currentIndex()))
        self.cboProduct.setCurrentText(self.cboProduct.currentText())
