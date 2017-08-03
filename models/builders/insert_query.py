#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def insert_query(model_def):
    name = model_def["name"]
    fld_count = len(model_def["fields"])
    stringf = ""
    stringv = ""
    for idx, field in enumerate(model_def["fields"]):
        if (idx + 1) == fld_count:
            stringf = field
            stringv = stringv + "?"
        else:
            stringf = field + ", "
            stringv = stringv + "?, "
    return "INSERT INTO {} ({}) VALUES ({});".format(name, stringf, stringv)
