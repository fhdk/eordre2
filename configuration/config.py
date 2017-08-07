#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Static configuration"""

import os

DEBUG_CONTACT = True
DEBUG_CUSTOMER = True
DEBUG_EMPLOYEE = True
DEBUG_SALELINE = True
DEBUG_PRODUCT = True
DEBUG_REPORT = True
DEBUG_CALCULATOR = True
DEBUG_SETTINGS = True
DEBUG_VISIT = True

DEBUG_QUERY = False

CONN_CHECK = ["https://bitbucket.org", "https://github.com", "https://wikipedia.org"]
COUNTRIES = [("dk", "Danmark"), ("no", "Norge"), ("s", "Sverige")]
HOME = os.path.expanduser("~")
APP_DATA = "./appdata"
DBPATH = APP_DATA + "/app.db"
LOGPATH = APP_DATA + "/app.log"
TABLES = ["contact", "customer", "employeeid", "visit", "orderline", "product", "reportid", "settings"]
CSVDATA = [("Kontakter", "contact"), ("Kunder", "customer"),
           ("Ordrelinjer", "orderline"), ("Ordrer", "visit"), ("Rapporter", "reportid")]
DECODE_HTTP = "ISO-8859-1"
