#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Static configuration"""

import os

CONN_CHECK = ["https://bitbucket.org", "https://github.com", "https://wikipedia.org"]
COUNTRIES = ["dk", "no", "s"]
HOME = os.path.expanduser("~")
APP_DATA = "./.appdata"
DBPATH = APP_DATA + "/app.db"
LOGPATH = APP_DATA + "/app.log"
TABLES = ["contacts", "customers", "employees", "visits", "orderlines", "products", "reports", "settings"]
CSVDATA = [("Kontakter", "contacts"), ("Kunder", "customers"), ("Ordrer", "visits"), ("Ordrelinjer", "orderlines"),
           ("Rapporter", "reports")]
DECODE = "ISO-8859-1"








