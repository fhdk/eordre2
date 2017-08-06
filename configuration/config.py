#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Static configuration"""

import os

DEBUG_CONTACT = False
DEBUG_CUSTOMER = False
DEBUG_EMPLOYEE = False
DEBUG_ORDERLINE = False
DEBUG_PRODUCT = False
DEBUG_QUERY = False
DEBUG_REPORT = True
DEBUG_CALCULATOR = True
DEBUG_SETTINGS = False
DEBUG_VISIT = False

CONN_CHECK = ["https://bitbucket.org", "https://github.com", "https://wikipedia.org"]
COUNTRIES = [("dk", "Danmark"), ("no", "Norge"), ("s", "Sverige")]
HOME = os.path.expanduser("~")
APP_DATA = "./appdata"
DBPATH = APP_DATA + "/app.db"
LOGPATH = APP_DATA + "/app.log"
TABLES = ["contact", "customer", "employee", "visit", "orderline", "product", "report", "settings"]
CSVDATA = [("Kontakter", "contact"), ("Kunder", "customer"),
           ("Ordrelinjer", "orderline"), ("Ordrer", "visit"), ("Rapporter", "report")]
DECODE_HTTP = "ISO-8859-1"
