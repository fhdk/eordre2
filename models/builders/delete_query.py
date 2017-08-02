#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def delete_query(model_def, where_list):
    name = model_def["name"]
    whr_count = len(where_list)
    string = ""
    # where 'field' operator
    for idx, d_item in enumerate(where_list):
        field = d_item[0]
        operator = d_item[1].upper()
        andor = ""
        if len(d_item) == 3:
            andor = d_item[2].upper()
        if (idx + 1) == whr_count:
            string = string + " {} {} ?".format(field, operator)
        else:
            if andor:
                string = string + " {} {} ? {}".format(field, operator, andor)
            else:
                string = string + " {} {} ?".format(field, operator)

    return "DELETE FROM {} WHERE {};".format(name, string)
