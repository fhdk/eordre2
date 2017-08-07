#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Visit Dialog Module
"""
from PyQt5.QtWidgets import QDialog

from models.visit import Visit
from models.product import Product

from resources.visit_dialog_rc import Ui_VisitDialog


class VisitDialog(QDialog, Ui_VisitDialog):
    """
    Dialog for creating a new visit
    """

    def __init__(self, report, customer, employee, workdate, parent=None):
        """
        Initialize
        Args:
            report: populated Report object class
            customer: current customer from main
            employee: current employee from main
            workdate: workdate
            parent:
        """
        super(VisitDialog, self).__init__(parent)
        self.setupUi(self)

        self.Report = report  # this is an object class
        self.Visit = Visit()  # Create an OrderVisit object
        self.Product = Product()  # Create Product object

        self.customerid = customer["customerid"]
        self.employeeid = employee["employeeid"]
        self.reportid = self.Report.report["reportid"]
        self.workdate = workdate

        # If customerid need special Settings on prices
        factor = customer["factor"]
        if factor > 0.0:
            for item in self.Product.product_list:
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
        self.txtCompany.setText(customer["company"])
        # connect to signals
        self.buttonCreateOrderLine.clicked.connect(self.button_create_sale_action)
        self.buttonCreateOrderVisit.clicked.connect(self.button_create_ordervisit_action)

    def button_create_sale_action(self):
        """Slot for Create Order Button clicked signal"""
        pass

    def button_create_ordervisit_action(self):
        """Slot for Create Order Button clicked signal"""
        self.visit.create(self.reportid, self.employeeid, self.customerid, self.workdate)
