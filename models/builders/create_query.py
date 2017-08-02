#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def create_query(model_def):
    string = ""
    name = model_def["name"]
    fld_count = len(model_def["fields"])

    for idx, field_def in enumerate(zip(model_def["fields"], model_def["types"])):
        field = field_def[0]
        define = field_def[1]
        if (idx + 1) == fld_count:
            string = string + "{} {}".format(field, define)
        else:
            string = string + "{} {}, ".format(field, define)

    return "CREATE TABLE IF NOT EXISTS {} ({});".format(name, string)
