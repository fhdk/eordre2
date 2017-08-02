#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Sqlite database functions"""

import sqlite3

from configuration import config


def exist_table(tablename):
    """Check database if tablename exist
    :param tablename:
    """
    statement = "select name from sqlite_master " \
                "where type='{}' and name='{}';".format("table", tablename)
    conn = sqlite3.connect(config.DBPATH)
    with conn:
        cur = conn.cursor()
        cur.execute(statement)
        t = cur.fetchone()
        if t:
            return True
    return False
