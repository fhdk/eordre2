#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import sqlite3

db = sqlite3.connect("../.appdata/test.db")

dates = [("2017-02-23",), ("2017-02-24",), ("2017-02-25",), ("2017-02-26",), ("2017-02-27",), ("2017-02-28",),
         ("2017-02-29",),
         ("2017-03-01",), ("2017-03-02",), ("2017-03-06",), ("2017-06-03",), ("2017-04-04",), ("2017-04-05",),
         ("2017-05-04",),
         ("2017-05-05",)]

with db:
    db.execute("DROP TABLE IF EXISTS reports")
    db.commit()
    db.execute("CREATE TABLE reports (repdate TEXT)")
    db.commit()
    for d in dates:
        print(d)
        db.execute("INSERT INTO reports VALUES (?)", d)

    db.commit()
